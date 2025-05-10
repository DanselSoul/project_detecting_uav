import cv2
import os
import time
from collections import deque
from fastapi.responses import StreamingResponse
from backend.app.yolo.uav_detector import detect_and_track
from backend.app.state.detection_state import clear_cam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "..", "sample_videos")
PLACEHOLDER_JP = os.path.join(VIDEO_DIR, "placeholder.jpg")
CONF_THRESHOLD = 0.3

# Буфер для хранения последних кадров по каждой камере
frame_buffer = {}  # cam_id: deque(maxlen=1500)

def video_generator(cam_id: int = 1, save_to_buffer=True):
    video_file = os.path.join(VIDEO_DIR, f"video_{cam_id}.mp4")

    if cam_id not in frame_buffer:
        frame_buffer[cam_id] = deque(maxlen=1500)  # 60 сек * 25 fps

    if not os.path.isfile(video_file):
        clear_cam(cam_id)
        placeholder = cv2.imread(PLACEHOLDER_JP)
        while True:
            frame = placeholder.copy()
            cv2.putText(frame, f"CAM-{cam_id} NO SIGNAL", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, jpg = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
            time.sleep(0.2)

    cap = cv2.VideoCapture(video_file)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        processed = detect_and_track(frame, camera_id=cam_id, conf_threshold=CONF_THRESHOLD)

        if save_to_buffer:
            frame_buffer[cam_id].append(processed.copy())

        cv2.putText(processed, f"CAM-{cam_id}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        _, jpg = cv2.imencode(".jpg", processed)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
        time.sleep(0.03)

    cap.release()

def replay_generator(cam_id: int):
    if cam_id not in frame_buffer or not frame_buffer[cam_id]:
        yield b""  # пусто
        return

    for frame in list(frame_buffer[cam_id]):
        _, jpg = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
        time.sleep(0.04)  # 25 fps
