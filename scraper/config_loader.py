import yaml
import json
import logging
from urllib.parse import urlparse
from typing import Any


def load_config(path: str) -> dict[str, Any]:
    """Load and return the YAML configuration file."""
    with open(path) as fh:
        config = yaml.safe_load(fh)
    logging.info(json.dumps({"event_type": "config_loaded", "path": path}))
    return config


def infer_store_name(url: str) -> str:
    """Derive a human-readable store name from the URL's domain.

    For example:
        https://www.costco.ca/…  →  costco
        https://www.canadacomputers.com/…  →  canadacomputers
    """
    netloc = urlparse(url).netloc  # e.g. "www.costco.ca"
    # Strip common prefixes/suffixes to get the brand token
    parts = netloc.replace("www.", "").split(".")
    return parts[0] if parts else netloc
