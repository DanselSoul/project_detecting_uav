import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from backend.app.db import SessionLocal
from backend.app.models.detection_record import DetectionRecord
from datetime import datetime
from time import time

from backend.app.state.detection_state import is_new_track, push_event

track_id_map = {}
model = YOLO("backend/app/yolo/yolo11n_best.pt")
_trackers = {}

def get_tracker(camera_id: int):
    if camera_id not in _trackers:
        _trackers[camera_id] = DeepSort(
            max_age=5, n_init=4, max_cosine_distance=0.4,
            embedder="mobilenet", half=True, bgr=True, embedder_gpu=True
        )
    return _trackers[camera_id]

def detect_and_track(frame, camera_id: int, conf_threshold=0.5):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(rgb, conf=conf_threshold, verbose=False)[0]

    dets = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0:
            continue
        dets.append(((x1, y1, w, h), float(box.conf[0]), int(box.cls[0])))

    tracker = get_tracker(camera_id)
    tracks = tracker.update_tracks(dets, frame=frame)

    for tr in tracks:
        if not tr.is_confirmed():
            continue

        local_tid = int(tr.track_id)
        key = (camera_id, local_tid)

        if key not in track_id_map:
            global_tid = camera_id * 10**13 + int(time() * 1000)
            track_id_map[key] = global_tid
        else:
            global_tid = track_id_map[key]

        if is_new_track(camera_id, global_tid):
            push_event(camera_id, global_tid)
            db = SessionLocal()
            print(f"[TRACK] Camera {camera_id}, global_tid={global_tid}, local_tid={local_tid}")
            db.add(DetectionRecord(
                cam=camera_id,
                track_id=global_tid,
                detected=True,
                is_validated=False,
                timestamp=datetime.utcnow()
            ))
            db.commit()
            print(f"[DB] Detection saved: cam={camera_id}, global_tid={global_tid}")
            db.close()

        x1, y1, x2, y2 = map(int, tr.to_ltrb())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame, f"ID {global_tid}", (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )

    return frame
