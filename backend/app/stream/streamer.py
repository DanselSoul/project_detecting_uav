import cv2
import os
import time
import threading
from fastapi.responses import StreamingResponse
from backend.app.yolo.uav_detector import detect_and_track
from backend.app.state.detection_state import clear_cam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "..", "sample_videos")
PLACEHOLDER_JPG = os.path.join(VIDEO_DIR, "placeholder.jpg")
CONF_THRESHOLD = 0.3

camera_threads = {}
frame_data = {}  # cam_id: {"frame": bytes, "lock": threading.Lock()}

def _camera_worker(cam_id: int, video_file: str):
    if not os.path.isfile(video_file):
        placeholder = cv2.imread(PLACEHOLDER_JPG)
        while True:
            frame = placeholder.copy()
            cv2.putText(frame, f"CAM-{cam_id} NO SIGNAL", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, jpg = cv2.imencode(".jpg", frame)
            with frame_data[cam_id]["lock"]:
                frame_data[cam_id]["frame"] = jpg.tobytes()
            time.sleep(0.2)
        return

    cap = cv2.VideoCapture(video_file)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        processed = detect_and_track(frame, camera_id=cam_id, conf_threshold=CONF_THRESHOLD)
        cv2.putText(processed, f"CAM-{cam_id}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        _, jpg = cv2.imencode(".jpg", processed)
        with frame_data[cam_id]["lock"]:
            frame_data[cam_id]["frame"] = jpg.tobytes()
        time.sleep(0.03)
    cap.release()

def ensure_camera_stream(cam_id: int):
    if cam_id not in camera_threads:
        video_file = os.path.join(VIDEO_DIR, f"video_{cam_id}.mp4")
        frame_data[cam_id] = {"frame": b"", "lock": threading.Lock()}
        thread = threading.Thread(target=_camera_worker, args=(cam_id, video_file), daemon=True)
        camera_threads[cam_id] = thread
        thread.start()

def video_generator(cam_id: int):
    ensure_camera_stream(cam_id)
    while True:
        with frame_data[cam_id]["lock"]:
            frame = frame_data[cam_id]["frame"]
        if frame:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.03)
