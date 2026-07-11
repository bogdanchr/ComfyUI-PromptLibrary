import hashlib
import json
import os
import random
import threading
from pathlib import Path

_STATE_PATH = Path(__file__).resolve().parents[3] / "data" / "state" / "unique_state.json"
_LOCK = threading.Lock()

def _signature(lines):
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()

def _load():
    if not _STATE_PATH.is_file():
        return {}
    try:
        data = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def _save(state):
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = _STATE_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, _STATE_PATH)

def reset_unique_state(file_path=None, folder_path=None):
    with _LOCK:
        state = _load()
        before = len(state)
        if file_path:
            state.pop(str(Path(file_path).expanduser().resolve()), None)
        elif folder_path:
            folder = str(Path(folder_path).expanduser().resolve())
            state = {k: v for k, v in state.items() if not (k == folder or k.startswith(folder + os.sep))}
        else:
            state = {}
        _save(state)
        return before - len(state)

def pick_unique_line(file_path, lines, seed):
    if not lines:
        raise ValueError("Cannot select from an empty list")
    absolute = str(Path(file_path).expanduser().resolve())
    signature = _signature(lines)
    with _LOCK:
        state = _load()
        entry = state.get(absolute, {})
        remaining = entry.get("remaining", [])
        cycle = int(entry.get("cycle", 0))
        if entry.get("signature") != signature:
            remaining, cycle = [], 0
        valid = set(range(len(lines)))
        remaining = [idx for idx in remaining if idx in valid]
        if not remaining:
            remaining = list(range(len(lines)))
            random.Random(seed + cycle * 1_000_003).shuffle(remaining)
            cycle += 1
        selected = remaining.pop(0)
        state[absolute] = {"signature": signature, "remaining": remaining, "cycle": cycle}
        _save(state)
    return lines[selected], selected
