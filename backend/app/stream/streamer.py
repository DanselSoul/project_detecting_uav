import cv2
import os
import time
from fastapi.responses import StreamingResponse
from backend.app.yolo.uav_detector import detect_and_track
from backend.app.state.detection_state import clear_cam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "..", "sample_videos")
PLACEHOLDER_JP = os.path.join(VIDEO_DIR, "placeholder.jpg")
CONF_THRESHOLD = 0.3

def video_generator(cam_id: int = 1):
    video_file = os.path.join(VIDEO_DIR, f"video_{cam_id}.mp4")
    
    if not os.path.isfile(video_file):
        clear_cam(cam_id)
        placeholder = cv2.imread(PLACEHOLDER_JP)
        while True:
            frame = placeholder.copy()
            cv2.putText(frame, f"CAM-{cam_id} NO SIGNAL", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, jpg = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   jpg.tobytes() + b"\r\n")
            time.sleep(0.2)

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
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               jpg.tobytes() + b"\r\n")
        time.sleep(0.03)

    cap.release()
