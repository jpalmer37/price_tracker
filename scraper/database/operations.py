from price_tracker.database.models import PriceSnapshot, Store, Item
from sqlalchemy.orm.exc import IntegrityError
import re 
from datetime import datetime 
import logging

def _get_store_name(url):
    result = re.search('^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\.\/\n]+)', url)
    return result.group(1) if result else None

def _get_store_base_url(url):
    result = re.search('^(?:https?:\/\/)?(?:[^@\/\n]+@)?((?:www\.)?[^:\/\n]+)\/', url)
    return result.group(1) if result else None


def get_or_create_store(session, store_url):
    """Get existing store or create new one if it doesn't exist"""

    if not store_url:
        raise ValueError("Store name and base URL are required")
    
    store_name = _get_store_name(store_url)
    store_base_url = _get_store_base_url(store_url)

    if not store_name:
        raise ValueError("Store name could not be extracted from URL")
     
    try:
        store = session.query(Store).filter(Store.name == store_name).first()

        if store is None:
            store = Store(
                name=store_name,
                base_url=store_base_url
            )
            session.add(store)
            session.flush()
            
        return store
        
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating store: {str(e)}")

def get_or_create_item(session, item_url, item_name, is_active):
    """Get existing store or create new one if it doesn't exist"""

    try:
        item = session.query(Item).filter(Item.url == item_url).first()

        if not item:
            store = get_or_create_store(session, item_url)

            item = Item(name=item_name, url=item_url, is_active=is_active, store_id=store.primary_id)
            session.add(item)
            session.flush()
            logging.info(f"Created new item: {item}")

    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating item: {str(e)}")
    return item

def add_price_snapshot(session, item_url, item_name, price):
        
    item = get_or_create_item(session, item_url, item_name=item_name, is_active=True)

    date_time = datetime.now()

    try: 
        snapshot = PriceSnapshot(timestamp=date_time, price=price, item_id=item.primary_id)
        session.add(snapshot)
        session.flush()
        logging.debug(f"Created new price snapshot: {snapshot}")
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Error creating price snapshot: {str(e)}")

def get_item_history( item_id, limit=20):
    with self.db_manager.session_scope() as session:
        return session.query(PriceSnapshot)\
                        .filter(PriceSnapshot.item_id == item_id)\
                        .order_by(PriceSnapshot.timestamp.desc())\
                        .limit(limit).all()