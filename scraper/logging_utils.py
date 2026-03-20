import json
import logging
import sys
from typing import Any


def setup_json_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, handlers=[logging.StreamHandler(sys.stdout)], force=True)


def log_event(level: int, event_type: str, **payload: Any) -> None:
    logging.log(level, json.dumps({"event_type": event_type, **payload}, default=str))
