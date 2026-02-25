from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from price_tracker.models.price_snapshot import PriceSnapshot


class DatabaseConnectionService:
    def __init__(self, config_service):
        self.engine = create_engine(config_service.get_database_url())
        self.Session = sessionmaker(bind=self.engine)
    
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

class DatabaseOperationService:

    def __init__(self, connection_service):
        self.connection = connection_service
    def add_price_snapshot(self, item_id, price):
        with self.connection.session_scope() as session:
            snapshot = PriceSnapshot(item_id=item_id, price=price)
        session.add(snapshot)
