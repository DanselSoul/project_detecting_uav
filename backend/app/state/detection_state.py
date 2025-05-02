# backend/app/state/detection_state.py
from threading import Lock

# cam_id -> last_detection_id
detection_flags = {}
lock = Lock()

def set_detection(cam_id: int, detection_id: int):
    with lock:
        detection_flags[cam_id] = detection_id

def pop_detection(cam_id: int):
    with lock:
        return detection_flags.pop(cam_id, None)
