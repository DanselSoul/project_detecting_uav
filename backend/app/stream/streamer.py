import cv2
import os
import time
import threading
import queue
from collections import deque
from backend.app.yolo.uav_detector import detect_and_track

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(BASE_DIR, "sample_videos")
PLACEHOLDER_PATH = os.path.join(VIDEO_DIR, "placeholder.jpg")

CONF_THRESHOLD = 0.5
FRAME_QUEUE_SIZE = 25

def video_generator(camera_id: int = 1):
    video_path = os.path.join(VIDEO_DIR, f"video_{camera_id}.mp4")

    # === Если видео нет — переключаемся на заглушку ===
    if not os.path.isfile(video_path):
        print(f"[WARN] Video for cam {camera_id} not found, using placeholder.")

        if not os.path.isfile(PLACEHOLDER_PATH):
            raise FileNotFoundError(f"Placeholder image not found at: {PLACEHOLDER_PATH}")

        placeholder_img = cv2.imread(PLACEHOLDER_PATH)
        if placeholder_img is None:
            raise RuntimeError("Failed to load placeholder image.")

        while True:
            annotated = placeholder_img.copy()
            cv2.putText(annotated, f"CAM-{camera_id} | Нет сигнала", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            _, jpeg = cv2.imencode(".jpg", annotated)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
            time.sleep(0.2)

    # === Основной путь: видео найдено ===
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Can't open video: {video_path}")

    frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
    processed_frame = [None]
    fps_history = deque(maxlen=10)
    stop_flag = threading.Event()

    def processor():
        prev_time = time.time()
        while not stop_flag.is_set():
            try:
                frame = frame_queue.get(timeout=1)
            except queue.Empty:
                continue

            if frame is None:
                break

            result = detect_and_track(frame, camera_id=camera_id, conf_threshold=CONF_THRESHOLD)
            end = time.time()

            processed_frame[0] = result
            fps = 1.0 / (end - prev_time)
            prev_time = end
            fps_history.append(fps)

    thread = threading.Thread(target=processor, daemon=True)
    thread.start()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if not frame_queue.full():
                frame_queue.put(frame)

            if processed_frame[0] is not None:
                avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0.0
                annotated = processed_frame[0].copy()
                cv2.putText(annotated, f"CAM-{camera_id} | FPS: {avg_fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                _, jpeg = cv2.imencode(".jpg", annotated)
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")

            time.sleep(0.005)
    finally:
        stop_flag.set()
        frame_queue.put(None)
        thread.join()
        cap.release()
