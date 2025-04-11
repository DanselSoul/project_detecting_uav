from fastapi import FastAPI, WebSocket, Query
import asyncio
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.app.routes import auth
from starlette.websockets import WebSocketState

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Имитация базы данных для хранения записей о детекции ---
detection_records = []  # Список для хранения записей

# Словарь для хранения состояния "остановки" уведомлений по камерам:
paused_alerts = {}  # key: cam_id, value: datetime до которого уведомления отключены

def is_camera_in_cooldown(cam_id: int) -> bool:
    if cam_id in paused_alerts:
        return datetime.now() < paused_alerts[cam_id]
    return False

def set_camera_cooldown(cam_id: int, cooldown_seconds: int = 60):
    paused_alerts[cam_id] = datetime.now() + timedelta(seconds=cooldown_seconds)


app.include_router(auth.router, prefix="/auth")

# --- WebSocket-эндпоинт для отправки уведомлений ---
@app.websocket("/ws/alerts")
async def alert_socket(websocket: WebSocket):
    await websocket.accept()
    cam_id = 1  # В данном примере работа ведётся для камеры 1
    try:
        while True:
            # Если камера в режиме "остановки" – пропускаем отправку уведомления
            if is_camera_in_cooldown(cam_id):
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

# --- Эндпоинт для видеопотока (оставляем без изменений) ---
@app.get("/video-feed")
def video_feed(cam: int = Query(1)):
    # Здесь функция video_generator должна возвращать видеопоток для камеры cam
    from backend.app.stream.streamer import video_generator
    return StreamingResponse(video_generator(camera_id=cam), media_type="multipart/x-mixed-replace; boundary=frame")

# --- Модель данных для записи детекции ---
class AlertRecord(BaseModel):
    cam: int
    detected: bool

# --- Эндпоинт для сохранения информации о детекции ---
@app.post("/alert/detection")
async def record_detection(record: AlertRecord):
    # Создаем запись (в реальном приложении здесь можно использовать ORM для вставки в БД)
    detection_records.append({
        "cam": record.cam,
        "detected": record.detected,
        "timestamp": datetime.now()
    })
    print(f"Detection recorded: {detection_records[-1]}")
    
    # Устанавливаем режим "остановки" уведомлений для камеры на 1 минуту
    set_camera_cooldown(record.cam, 60)
    return {"status": "ok", "message": "Detection recorded, alerts suspended for 1 minute"}
