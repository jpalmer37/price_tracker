import logging
import json
import sys


def setup_json_logging(level: str = "INFO") -> None:
    """Configure the root logger to emit JSON-formatted lines to stdout."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers.clear()
    root.addHandler(handler)


def log_event(level: str, event_type: str, **kwargs) -> None:
    """Emit a single JSON log line with an ``event_type`` key."""
    payload = {"event_type": event_type, **kwargs}
    getattr(logging, level, logging.info)(json.dumps(payload))
