import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from sqlalchemy.exc import IntegrityError

from scraper.logging_utils import log_event
from scraper.parsers import infer_store_name

from .models import Item, PriceSnapshot, Store


def _get_store_name(url):
    try:
        return infer_store_name(url)
    except ValueError:
        hostname = (urlparse(url).hostname or "").lower().removeprefix("www.")
        return hostname.split(".")[0] if hostname else None


def _get_store_base_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return None

    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def _normalize_price(price) -> Decimal | None:
    if price is None:
        return None

    if isinstance(price, Decimal):
        return price

    if isinstance(price, (int, float)):
        return Decimal(str(price))

    cleaned_price = "".join(character for character in str(price) if character.isdigit() or character == ".")
    if not cleaned_price:
        return None

    try:
        return Decimal(cleaned_price)
    except InvalidOperation as exc:
        raise ValueError(f"Error parsing price: {price}") from exc


def get_or_create_store(session, store_url):
    """Get existing store or create new one if it doesn't exist"""

    if not store_url:
        raise ValueError("Store name and base URL are required")
    
    store_name = _get_store_name(store_url)
    store_base_url = _get_store_base_url(store_url)

    if not store_name:
        raise ValueError("Store name could not be extracted from URL")
     
    try:
        store = session.query(Store).filter(Store.base_url == store_base_url).first()

        if store is None:
            store = Store(
                name=store_name,
                base_url=store_base_url
            )
            session.add(store)
            session.flush()
            log_event(logging.INFO, "store_created", store_name=store.name, base_url=store.base_url)
            
        return store
        
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating store: {str(e)}")

def get_or_create_item(session, item_url, item_name, is_active=True):
    """Get existing store or create new one if it doesn't exist"""

    try:
        item = session.query(Item).filter(Item.url == item_url).first()

        if not item:
            store = get_or_create_store(session, item_url)

            item = Item(name=item_name, url=item_url, is_active=is_active, store_id=store.id)
            session.add(item)
            session.flush()
            log_event(logging.INFO, "item_created", item_url=item.url, item_name=item.name, store_name=store.name)
        else:
            item.name = item_name or item.name
            item.is_active = is_active

    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating item: {str(e)}")
    return item

def add_price_snapshot(session, item_url, item_name, price):
        
    item = get_or_create_item(session, item_url, item_name=item_name, is_active=True)
    normalized_price = _normalize_price(price)
    date_time = datetime.now()

    try: 
        snapshot = PriceSnapshot(timestamp=date_time, price=normalized_price, item_id=item.id)
        session.add(snapshot)
        session.flush()
        log_event(
            logging.INFO,
            "price_snapshot_created",
            item_url=item.url,
            item_name=item.name,
            price=str(normalized_price) if normalized_price is not None else None,
            timestamp=date_time.isoformat(),
        )
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating price snapshot: {str(e)}")

    return snapshot

def get_item_history(session, item_id, limit=20):
    return session.query(PriceSnapshot)\
                    .filter(PriceSnapshot.item_id == item_id)\
                    .order_by(PriceSnapshot.timestamp.desc())\
                    .limit(limit).all()
