from fastapi import FastAPI, WebSocket, Query, HTTPException, Depends
import asyncio
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from starlette.websockets import WebSocketState
from sqlalchemy.orm import Session
from backend.app.db import SessionLocal
from backend.app.models.detection_record import DetectionRecord
from backend.app.state.detection_state import is_detection_active  # проверка состояния детекции
from backend.app.state.detection_state import set_detection, clear_detection  # управление состоянием
from backend.app.routes import auth  # маршруты аутентификации

app = FastAPI()
app.include_router(auth.router, prefix="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Словарь для управления режимом "cooldown" уведомлений по камерам
paused_alerts = {}  # ключ: cam_id, значение: время до которого уведомления приостановлены

def is_camera_in_cooldown(cam_id: int) -> bool:
    if cam_id in paused_alerts:
        return datetime.now() < paused_alerts[cam_id]
    return False

def set_camera_cooldown(cam_id: int, cooldown_seconds: int = 60):
    paused_alerts[cam_id] = datetime.now() + timedelta(seconds=cooldown_seconds)

# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модель для валидации входящих данных детекции
class AlertRecord(BaseModel):
    cam: int
    detected: bool

# Обновлённый WebSocket‑эндпоинт, который извлекает параметр cam
@app.websocket("/ws/alerts")
async def alert_socket(websocket: WebSocket):
    await websocket.accept()
    cam_id_str = websocket.query_params.get("cam", "1")
    try:
        cam_id = int(cam_id_str)
    except ValueError:
        cam_id = 1

    try:
        while True:
            if is_camera_in_cooldown(cam_id):
                await asyncio.sleep(1)
                continue

            # Отправляем уведомление только если в кадре зафиксировано обнаружение БПЛА
            if not is_detection_active(cam_id):
                await asyncio.sleep(1)
                continue

            alert_message = f"alert: camera {cam_id}: drone detected"
            print("Sending message:", alert_message)
            await websocket.send_text(alert_message)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if websocket.client_state != WebSocketState.CLOSED:
            await websocket.close()
        print("WebSocket connection closed")

# Остальные эндпоинты (видеопоток и запись детекции) остаются без изменений
@app.get("/video-feed")
def video_feed(cam: int = Query(1)):
    from backend.app.stream.streamer import video_generator
    return StreamingResponse(video_generator(camera_id=cam), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/alert/detection")
async def record_detection(record: AlertRecord, db: Session = Depends(get_db)):
    detection = DetectionRecord(cam=record.cam, detected=record.detected)
    db.add(detection)
    db.commit()
    db.refresh(detection)
    print(f"Detection recorded: {detection.id} for camera {detection.cam} at {detection.timestamp}")
    set_camera_cooldown(record.cam, 60)
    return {"status": "ok", "message": "Detection recorded, alerts suspended for 1 minute"}
