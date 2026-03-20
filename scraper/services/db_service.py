from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from scraper.database.operations import add_price_snapshot


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

    def add_price_snapshot(self, item_url, item_name, price):
        with self.connection.session_scope() as session:
            add_price_snapshot(session, item_url=item_url, item_name=item_name, price=price)
