import json
import logging
import re
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Item, PriceSnapshot, Store


def _extract_store_name(url: str) -> str | None:
    """Return the brand token from a URL (e.g. 'costco' from 'https://www.costco.ca/…')."""
    match = re.search(
        r"^(?:https?://)?(?:[^@/\n]+@)?(?:www\.)?([^:./\n]+)", url
    )
    return match.group(1) if match else None


def _extract_base_url(url: str) -> str | None:
    match = re.search(
        r"^(?:https?://)?(?:[^@/\n]+@)?((?:www\.)?[^:/\n]+)", url
    )
    return match.group(1) if match else None


def get_or_create_store(session: Session, item_url: str) -> Store:
    """Return an existing Store or create one derived from *item_url*."""
    store_name = _extract_store_name(item_url)
    if not store_name:
        raise ValueError(f"Cannot extract store name from URL: {item_url}")

    store = session.query(Store).filter(Store.name == store_name).first()
    if store is None:
        store = Store(name=store_name, base_url=_extract_base_url(item_url))
        session.add(store)
        session.flush()
        logging.info(json.dumps({
            "event_type": "store_created",
            "store_name": store_name,
        }))
    return store


def get_or_create_item(
    session: Session, item_url: str, item_name: str, is_active: bool = True
) -> Item:
    """Return an existing Item or create one (auto-creating the Store if needed)."""
    item = session.query(Item).filter(Item.url == item_url).first()
    if item is None:
        store = get_or_create_store(session, item_url)
        item = Item(
            name=item_name, url=item_url, is_active=is_active, store_id=store.id
        )
        session.add(item)
        session.flush()
        logging.info(json.dumps({
            "event_type": "item_created",
            "item_name": item_name,
            "url": item_url,
        }))
    return item


def add_price_snapshot(
    session: Session, item_url: str, item_name: str, price: float | None
) -> PriceSnapshot:
    """Record a new PriceSnapshot for the given item."""
    item = get_or_create_item(session, item_url, item_name=item_name)
    snapshot = PriceSnapshot(
        timestamp=datetime.now(), price=price, item_id=item.id
    )
    session.add(snapshot)
    session.flush()
    logging.info(json.dumps({
        "event_type": "price_snapshot_added",
        "item_name": item_name,
        "price": str(price),
    }))
    return snapshot


def get_item_history(
    session: Session, item_id: int, limit: int = 20
) -> list[PriceSnapshot]:
    """Return the most recent *limit* snapshots for an item."""
    return (
        session.query(PriceSnapshot)
        .filter(PriceSnapshot.item_id == item_id)
        .order_by(PriceSnapshot.timestamp.desc())
        .limit(limit)
        .all()
    )