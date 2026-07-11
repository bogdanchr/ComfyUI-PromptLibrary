"""Process-local runtime state used to invalidate ComfyUI execution cache.

Text files already use mtime-aware caching, but ComfyUI may reuse a node's old
output when none of its visible inputs changed.  A library revision is bumped by
Utilities so Prompt Library's IS_CHANGED value changes on the next queue run.
"""
from threading import RLock

_LOCK = RLock()
_LIBRARY_REVISION = 0


def get_library_revision() -> int:
    with _LOCK:
        return _LIBRARY_REVISION


def bump_library_revision() -> int:
    global _LIBRARY_REVISION
    with _LOCK:
        _LIBRARY_REVISION += 1
        return _LIBRARY_REVISION
