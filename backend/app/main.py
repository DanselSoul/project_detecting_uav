from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime
from sqlalchemy import and_

from backend.app.routes import auth
from backend.app.stream.streamer import video_generator, replay_generator
from backend.app.state.detection_state import get_events
from backend.app.db import SessionLocal
from backend.app.models.detection_record import DetectionRecord, ValidationRecord

startup_time = datetime.utcnow()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/video-feed")
def video_feed(cam: int = Query(1)):
    return StreamingResponse(
        video_generator(cam),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/replay")
def replay(cam: int = Query(1)):
    return StreamingResponse(
        replay_generator(cam),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/active-alerts")
def get_active():
    print("Startup time:", startup_time.isoformat())
    db = SessionLocal()
    records = db.query(DetectionRecord).filter(
        and_(
            DetectionRecord.is_validated == False,
            DetectionRecord.timestamp > startup_time
        )
    ).all()
    db.close()

    result = {}
    for rec in records:
        result.setdefault(rec.cam, []).append(rec.track_id)
    return result

@app.websocket("/ws/alerts")
async def alerts_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(0.5)
            events = get_events()
            for cam_id, track_ids in events.items():
                for tid in track_ids:
                    await websocket.send_text(f"camera {cam_id}: track {tid} detected")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")

@app.post("/validate")
def validate_detection(
    cam: int = Body(...),
    track_id: int = Body(...),
    validated: bool = Body(...),
    comment: str = Body(default=None),
    decision_source: str = Body(default="operator")
):
    db = SessionLocal()

    detection = db.query(DetectionRecord).filter_by(cam=cam, track_id=track_id).first()
    if not detection:
        db.close()
        raise HTTPException(status_code=404, detail="Detection not found")

    validation = ValidationRecord(
        detection_id=detection.id,
        validated=validated,
        track_id=track_id,
        camera_id=cam,
        decision_source=decision_source,
        comment=comment
    )
    db.add(validation)
    detection.is_validated = True

    db.commit()
    db.close()
    return {"status": "ok", "validated": validated}
