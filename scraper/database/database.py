from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from scraper.database.models import Base
from .config import get_database_url


class Database:
    def __init__(self, database_url: str | None = None):
        connection_url = database_url or get_database_url()

        engine_kwargs = {"future": True}
        if not connection_url.startswith("sqlite"):
            engine_kwargs.update(
                {
                    "pool_size": 5,
                    "max_overflow": 10,
                    "pool_timeout": 30,
                    "pool_pre_ping": True,
                }
            )

        self.engine = create_engine(connection_url, **engine_kwargs)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
