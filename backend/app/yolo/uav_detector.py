import cv2
import numpy as np
from backend.app.yolo.yolo_model import model  # Импорт уже инициализированной модели
from deep_sort_realtime.deepsort_tracker import DeepSort
from backend.app.state.detection_state import set_detection

trackers = {}

def get_tracker(camera_id):
    if camera_id not in trackers:
        trackers[camera_id] = DeepSort(
            max_age=5,
            n_init=4,
            max_cosine_distance=0.4,
            embedder="mobilenet",
            half=True,
            bgr=True,
            embedder_gpu=True
        )
    return trackers[camera_id]

def detect_and_track(frame, camera_id=1, conf_threshold=0.5):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Используем уже загруженную модель
    results = model.predict(frame_rgb, conf=conf_threshold, verbose=False)[0]

    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0 or np.isnan(w) or np.isnan(h):
            continue
        detections.append(((x1, y1, w, h), conf, cls))

    tracker = get_tracker(camera_id)
    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        set_detection(camera_id)  # Устанавливаем, что дрон обнаружен

        x1, y1, x2, y2 = map(int, track.to_ltrb())
        track_id = track.track_id
        label = f"ID {track_id}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame