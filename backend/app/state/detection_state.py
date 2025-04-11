from threading import Lock

detection_flags = {}
lock = Lock()

def is_detection_active(cam_id: int):
    with lock:
        return detection_flags.get(cam_id, False)

def set_detection(cam_id: int):
    with lock:
        detection_flags[cam_id] = True

def clear_detection(cam_id: int):
    with lock:
        detection_flags[cam_id] = False

def get_detections():
    with lock:
        return detection_flags.copy()
