from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from config import get_database_url

class Database:
    def __init__(self, database_config={}):
        self.engine = create_engine(
			get_database_url(),
			pool_size=5,
			max_overflow=10,
			pool_timeout=30,
			pool_pre_ping=True
		)
        self.session_factory = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        database = self.session_factory()
        try:
            yield database
            database.commit()
        except SQLAlchemyError as e:
            database.rollback()
            raise e
        finally:
            database.close()
