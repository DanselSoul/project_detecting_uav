from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend.app.routes import auth
from backend.app.stream.streamer import video_generator
from backend.app.state.detection_state import (
    get_events, get_alarm_events, clear_cam, start_alarm, stop_alarm
)
from backend.app.db import SessionLocal
from fastapi import Depends
from backend.app.models.alarm_record import AlarmRecord
from backend.app.routes.auth import get_current_user
from backend.app.models.detection_record import DetectionRecord, ValidationRecord
from backend.app.models.user import User

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    db = SessionLocal()
    try:
        records = db.query(DetectionRecord).filter(
            and_(
                DetectionRecord.is_validated == False,
                DetectionRecord.timestamp > startup_time
            )
        ).all()
        result = {}
        for rec in records:
            result.setdefault(rec.cam, []).append(rec.track_id)
        return result
    finally:
        db.close()


@app.websocket("/ws/alerts")
async def alerts_socket(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            await asyncio.sleep(0.5)
            events = get_events()
            for cam_id, track_ids in events.items():
                for tid in track_ids:
                    detection = (
                        db.query(DetectionRecord)
                        .filter(DetectionRecord.cam == cam_id, DetectionRecord.track_id == tid)
                        .order_by(DetectionRecord.timestamp.desc())
                        .first()
                    )
                    if detection is None:
                        print(f"[WS] No detection found for cam={cam_id}, track_id={tid}")
                    else:
                        print(f"[WS] Sending alert for cam={cam_id}, track_id={tid}")
                    if detection and not detection.is_validated:
                        await websocket.send_text(f"camera {cam_id}: track {tid} detected")
            alarms = get_alarm_events()   # e.g. [1, -2, 3]
            for ev in alarms:
                if ev > 0:
                    cam = ev
                    print(f"[WS] Sending ALARM START for cam={cam}")
                    await websocket.send_text(f"alarm_start camera {cam}")
                else:
                    cam = abs(ev)
                    print(f"[WS] Sending ALARM STOP  for cam={cam}")
                    await websocket.send_text(f"alarm_stop camera {cam}")
    except WebSocketDisconnect:
        pass
    finally:
        db.close()


@app.post("/validate")
def validate_detection(
    cam: int = Body(...),
    track_id: int = Body(...),
    validated: bool = Body(...),
    comment: str = Body(default=None),
    decision_source: str = Body(default="operator"),
    current_user: User = Depends(get_current_user, use_cache=False)
):
    db = SessionLocal()
    try:
        detection = db.query(DetectionRecord).filter_by(cam=cam, track_id=track_id).first()
        if not detection:
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
        action = "start" if validated else "stop"
        alarm = AlarmRecord(
            detection_id=detection.id,
            user_id=current_user.id,
            action=action
        )
        db.add(alarm)
        db.commit()
        if validated:
            start_alarm(cam)
            print(f"[WS] start_alarm called for cam={cam}")
        else:
            stop_alarm(cam)
            print(f"[WS] stop_alarm called for cam={cam}")
        return {"status": "ok", "validated": validated}
    finally:
        db.close()

@app.post("/alarm/stop")
def alarm_stop_endpoint(
    cam: int = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    stop_alarm(cam)
    return {"status": "ok"}

@app.get("/detections")
def get_recent_detections(
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
):
    recs = (
        db.query(DetectionRecord)
          .order_by(DetectionRecord.timestamp.desc())
          .limit(limit)
          .all()
    )
    # вернём упрощённую структуру
    return [
        {
          "camera": r.cam,
          "track_id": r.track_id,
          "timestamp": r.timestamp.isoformat(),
        }
        for r in recs
    ]