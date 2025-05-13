from threading import Lock
from collections import defaultdict
from typing import Dict, List, Set
_lock = Lock()

_notified_tracks: Dict[int, Set[int]] = defaultdict(set)
_new_events: Dict[int, List[int]] = defaultdict(list)

_active_alarms: Set[int] = set()
_new_alarm_events: List[int] = []


def is_new_track(cam_id: int, track_id: int) -> bool:
    with _lock:
        if track_id not in _notified_tracks[cam_id]:
            _notified_tracks[cam_id].add(track_id)
            return True
        return False


def push_event(cam_id: int, track_id: int) -> None:
    with _lock:
        _new_events[cam_id].append(track_id)


def get_events() -> Dict[int, List[int]]:
    with _lock:
        out = {cam: lst.copy() for cam, lst in _new_events.items()}
        _new_events.clear()
        return out


def clear_cam(cam_id: int) -> None:
    with _lock:
        _notified_tracks.pop(cam_id, None)
        _new_events.pop(cam_id, None)

def start_alarm(cam_id: int):
    with _lock:
        if cam_id not in _active_alarms:
            _active_alarms.add(cam_id)
            _new_alarm_events.append(+cam_id)


def stop_alarm(cam_id: int):
    with _lock:
        if cam_id in _active_alarms:
            _active_alarms.remove(cam_id)
            _new_alarm_events.append(-cam_id)


def get_alarm_events() -> List[int]:
    with _lock:
        ev = _new_alarm_events.copy()
        _new_alarm_events.clear()
        return ev
