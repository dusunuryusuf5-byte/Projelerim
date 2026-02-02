"""Logging helpers for PlayLingo.

Provides:
- setup_logging(level, capture_in_memory, memory_capacity, logfile)
- InMemoryLogHandler to keep a ring buffer of recent log records for diagnostics UI
- dump_logs_to_file(path)
"""
from __future__ import annotations

import logging
import threading
from collections import deque
from typing import Deque, List, Optional


class InMemoryLogHandler(logging.Handler):
    """A simple in-memory ring buffer log handler.

    Stores formatted messages up to `capacity` most recent entries.
    """

    def __init__(self, capacity: int = 200):
        super().__init__()
        self.capacity = int(capacity)
        self._lock = threading.RLock()
        self._buffer: Deque[str] = deque(maxlen=self.capacity)
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            with self._lock:
                self._buffer.append(msg)
        except Exception:
            self.handleError(record)

    def get_logs(self) -> List[str]:
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()


# Module-level singleton handler (created on first setup)
_memory_handler: Optional[InMemoryLogHandler] = None


def setup_logging(level: int = logging.INFO, capture_in_memory: bool = True, memory_capacity: int = 500, logfile: Optional[str] = None) -> None:
    """Configure root logging for the application.

    - level: logging level (int)
    - capture_in_memory: whether to keep an in-memory buffer (for diagnostics)
    - memory_capacity: number of messages to keep in memory
    - logfile: optional path to file to append logs
    """
    global _memory_handler
    root = logging.getLogger()
    # Avoid adding duplicate handlers on repeated calls
    if getattr(root, "_playlingo_configured", False):
        # Update level and logfile if needed
        root.setLevel(level)
        if logfile:
            fh = logging.FileHandler(logfile)
            fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            root.addHandler(fh)
        return

    root.setLevel(level)
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(ch)

    if logfile:
        fh = logging.FileHandler(logfile)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        root.addHandler(fh)

    if capture_in_memory:
        _memory_handler = InMemoryLogHandler(capacity=memory_capacity)
        _memory_handler.setLevel(level)
        root.addHandler(_memory_handler)

    root._playlingo_configured = True


def get_memory_handler() -> Optional[InMemoryLogHandler]:
    return _memory_handler


def dump_logs_to_file(path: str) -> None:
    mh = get_memory_handler()
    if mh is None:
        raise RuntimeError("In-memory logging not configured")
    logs = mh.get_logs()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(logs))
