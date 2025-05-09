import cv2
import os
import time
import threading
from collections import deque
from backend.app.yolo.uav_detector import detect_and_track

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "..", "sample_videos")
PLACEHOLDER = os.path.join(VIDEO_DIR, "placeholder.jpg")
CONF_THRESHOLD = 0.1
FPS = 10
BUFFER_SECONDS = 30

stream_pool = {}  # cam_id -> {buffer, lock, thread, last_frame}

def start_stream(cam_id: int):
    if cam_id in stream_pool:
        return

    buffer = deque(maxlen=BUFFER_SECONDS * FPS)
    lock = threading.Lock()
    last_frame = [None]

    video_path = os.path.join(VIDEO_DIR, f"video_{cam_id}.mp4")
    has_video = os.path.exists(video_path)

    def stream_loop():
        print(f"[THREAD] Starting stream for cam {cam_id}")
        if has_video:
            video = cv2.VideoCapture(video_path)
        else:
            placeholder = cv2.imread(PLACEHOLDER)

        while True:
            if has_video:
                ret, frame = video.read()
                if not ret:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
            else:
                frame = placeholder.copy()
                cv2.putText(frame, f"CAM-{cam_id} NO VIDEO", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            processed = detect_and_track(frame, cam_id, conf_threshold=CONF_THRESHOLD)
            _, jpg = cv2.imencode(".jpg", processed)
            jpg_bytes = jpg.tobytes()
            timestamp = time.time()

            with lock:
                buffer.append((timestamp, jpg_bytes))
                last_frame[0] = jpg_bytes

            time.sleep(1 / FPS)

    thread = threading.Thread(target=stream_loop, daemon=True)
    thread.start()

    stream_pool[cam_id] = {
        "buffer": buffer,
        "lock": lock,
        "thread": thread,
        "last_frame": last_frame
    }

def get_frame(cam_id: int, live=True, seek_time=None):
    start_stream(cam_id)
    stream = stream_pool[cam_id]
    buffer = stream["buffer"]
    lock = stream["lock"]
    last_frame = stream["last_frame"]

    if not live and seek_time is not None:
        target_time = time.time() - seek_time
        with lock:
            for ts, frame in buffer:
                if ts >= target_time:
                    return frame
        return None
    else:
        with lock:
            return last_frame[0]
