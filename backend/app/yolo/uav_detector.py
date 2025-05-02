import cv2
import numpy as np
from backend.app.yolo.yolo_model import model  # ваша загруженная YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from backend.app.state.detection_state import set_detection

# импортим сессию и модель
from backend.app.db import SessionLocal
from backend.app.models import DetectionRecord

# tracker factory...
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

def detect_and_track(frame, camera_id: int = 1, conf_threshold=0.5):
    # конвертация и предсказание YOLO
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(frame_rgb, conf=conf_threshold, verbose=False)[0]

    # собираем детекции в нужном формате
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0 or np.isnan(w) or np.isnan(h):
            continue
        detections.append(((x1, y1, w, h), conf, cls))

    # трекинг
    tracker = get_tracker(camera_id)
    tracks = tracker.update_tracks(detections, frame=frame)

    # если есть подтверждённый трек — пишем в БД
    found = False
    for track in tracks:
        if not track.is_confirmed(): continue
        found = True
        break

    if found:
        # сохраняем в БД
        db = SessionLocal()
        rec = DetectionRecord(cam=camera_id, detected=True)
        db.add(rec); db.commit(); db.refresh(rec)
        db.close()
        # кладём в state
        set_detection(camera_id, rec.id)

    return frame
