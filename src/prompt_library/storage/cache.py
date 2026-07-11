from pathlib import Path
from threading import RLock
from typing import Dict, List, Tuple

_FILE_CACHE: Dict[str, Tuple[int, List[str]]] = {}
_CACHE_LOCK = RLock()

def clear_prompt_cache(file_path=None) -> int:
    with _CACHE_LOCK:
        if file_path is None:
            count = len(_FILE_CACHE)
            _FILE_CACHE.clear()
            return count
        key = str(Path(file_path).expanduser().resolve())
        existed = int(key in _FILE_CACHE)
        _FILE_CACHE.pop(key, None)
        return existed

def read_raw_lines(file_path, reload_cache=False) -> List[str]:
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    mtime = path.stat().st_mtime_ns
    key = str(path)
    with _CACHE_LOCK:
        if not reload_cache and key in _FILE_CACHE:
            cached_mtime, cached_lines = _FILE_CACHE[key]
            if cached_mtime == mtime:
                return list(cached_lines)
    with path.open("r", encoding="utf-8-sig") as handle:
        lines = [line.rstrip("\r\n") for line in handle]
    with _CACHE_LOCK:
        _FILE_CACHE[key] = (mtime, list(lines))
    return lines
