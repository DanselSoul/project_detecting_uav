from threading import Lock
from collections import defaultdict
from typing import Optional, Dict, List

_lock = Lock()

_notified_tracks: Dict[int, set] = defaultdict(set)
_new_events: Dict[int, List[int]] = defaultdict(list)

def is_new_track(cam_id: int, track_id: int) -> bool:
    with _lock:
        if track_id not in _notified_tracks[cam_id]:
            _notified_tracks[cam_id].add(track_id)
            return True
        return False

def push_event(cam_id: int, track_id: int) -> None:
    with _lock:
        _new_events[cam_id].append(track_id)

def get_events(cam_id: Optional[int] = None):
    with _lock:
        if cam_id is None:
            all_ev = {c: lst.copy() for c, lst in _new_events.items()}
            _new_events.clear()
            return all_ev
        else:
            ev = _new_events.get(cam_id, []).copy()
            _new_events[cam_id].clear()
            return ev

def get_active_alerts() -> Dict[int, List[int]]:
    with _lock:
        return {cam_id: list(tids) for cam_id, tids in _notified_tracks.items()}

def clear_cam(cam_id: int) -> None:
    with _lock:
        _notified_tracks.pop(cam_id, None)
        _new_events.pop(cam_id, None)
