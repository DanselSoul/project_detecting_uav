from threading import Lock
import time

# Вместо булева значения храним время последнего обнаружения (или None, если обнаружения нет)
detection_flags = {}
lock = Lock()

def is_detection_active(cam_id: int, active_time: float = 2.0) -> bool:
    """
    Возвращает True, если последний вызов set_detection для камеры был не более active_time секунд назад.
    """
    with lock:
        ts = detection_flags.get(cam_id)
        if ts is None:
            return False
        return (time.time() - ts) < active_time

def set_detection(cam_id: int):
    """
    Фиксирует обнаружение, записывая текущее время.
    """
    with lock:
        detection_flags[cam_id] = time.time()

def clear_detection(cam_id: int):
    """
    Сбрасывает состояние обнаружения.
    """
    with lock:
        detection_flags[cam_id] = None

def get_detections():
    with lock:
        return detection_flags.copy()
