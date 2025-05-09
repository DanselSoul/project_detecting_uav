from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio


from backend.app.stream.streamer import video_generator
from backend.app.state.detection_state import get_events, get_active_alerts
from backend.app.db import SessionLocal
from backend.app.models.detection_record import DetectionRecord, ValidationRecord

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:5173"] — если хочешь строго
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/video-feed")
def video_feed(cam: int = Query(1)):
    return StreamingResponse(
        video_generator(cam),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/active-alerts")
def get_active():
    return get_active_alerts()

@app.websocket("/ws/alerts")
async def alerts_socket(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected")

    try:
        while True:
            await asyncio.sleep(0.5)
            events = get_events()  # ← только новые
            for cam_id, track_ids in events.items():
                for tid in track_ids:
                    await websocket.send_text(f"camera {cam_id}: track {tid} detected")
    except WebSocketDisconnect:
        print("[WS] Client disconnected")
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

    # Найти detection-запись
    detection = db.query(DetectionRecord).filter_by(cam=cam, track_id=track_id).first()
    if not detection:
        db.close()
        raise HTTPException(status_code=404, detail="Detection not found")

    # Создать запись подтверждения
    validation = ValidationRecord(
        detection_id=detection.id,
        validated=validated,
        track_id=track_id,
        camera_id=cam,
        decision_source=decision_source,
        comment=comment
    )
    db.add(validation)

    # Обновить detection
    detection.is_validated = True

    db.commit()
    db.close()
    return {"status": "ok", "validated": validated}
