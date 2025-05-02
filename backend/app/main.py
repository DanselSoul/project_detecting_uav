# backend/app/main.py
from fastapi import FastAPI, WebSocket, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
import asyncio

from backend.app.stream.streamer import video_generator
from backend.app.routes import auth
from backend.app.state.detection_state import pop_detection
from pydantic import BaseModel
from backend.app.db import SessionLocal
from backend.app.models import ValidationRecord

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/auth")

@app.get("/video-feed")
def video_feed(cam: int = Query(1)):
    return StreamingResponse(
        video_generator(camera_id=cam),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.websocket("/ws/alerts")
async def alert_socket(websocket: WebSocket, cam: int = Query(...)):
    await websocket.accept()
    try:
        while True:
            det_id = pop_detection(cam)
            if det_id:
                await websocket.send_text(f"{cam}|{det_id}")
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

class ValidationIn(BaseModel):
    detection_id: int
    validated: bool

@app.post("/validate")
def validate_detection(item: ValidationIn):
    db = SessionLocal()
    vr = ValidationRecord(
        detection_id=item.detection_id,
        validated=item.validated
    )
    db.add(vr)
    db.commit()
    db.close()
    return {"ok": True}
