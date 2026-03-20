from pathlib import Path

import yaml

from scraper.parsers import infer_store_name


def _normalize_items(raw_config: dict) -> list[dict]:
    if "items" in raw_config:
        items = raw_config.get("items") or []
    else:
        items = []
        for legacy_items in (raw_config.get("watchlist_by_store") or {}).values():
            items.extend(legacy_items or [])

    normalized_items = []
    for item in items:
        url = item["url"]
        normalized_items.append(
            {
                "url": url,
                "name": item.get("name"),
                "store_name": infer_store_name(url),
            }
        )

    return normalized_items


def _normalize_notification(raw_config: dict) -> dict:
    notification = raw_config.get("notification") or {}
    recipients = notification.get("recipients") or raw_config.get("email_recipients") or []

    return {
        "sender": notification.get("sender", "price-tracker@localhost"),
        "recipients": recipients,
        "latest_snapshots_limit": notification.get("latest_snapshots_limit", 5),
        "notable_drop_amount": notification.get("notable_drop_amount", 0),
        "notable_drop_percent": notification.get("notable_drop_percent", 10),
        "html_attachment_path": notification.get("html_attachment_path"),
    }


def load_config(config_file: str) -> dict:
    with Path(config_file).open(encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle) or {}

    return {
        "default_scan_interval": raw_config.get("default_scan_interval", 43200),
        "number_of_stored_snapshots": raw_config.get("number_of_stored_snapshots", 50),
        "page_load_wait_seconds": raw_config.get("page_load_wait_seconds", 5),
        "items": _normalize_items(raw_config),
        "notification": _normalize_notification(raw_config),
    }
