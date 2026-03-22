import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .config import get_database_url
from .models import Base


class Database:
    """Thin wrapper around a SQLAlchemy engine + session factory."""

    def __init__(self, url: str | None = None):
        self.url = url or get_database_url()
        engine_kwargs = {}
        if self.url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs.update({
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_pre_ping": True,
            })
        self.engine = create_engine(self.url, **engine_kwargs)
        self._session_factory = sessionmaker(bind=self.engine)
        logging.info(json.dumps({"event_type": "database_engine_created"}))

    def create_tables(self) -> None:
        """Create all tables that don't yet exist."""
        Base.metadata.create_all(self.engine)
        logging.info(json.dumps({"event_type": "database_tables_created"}))

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Provide a transactional scope around a series of operations."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            logging.error(json.dumps({
                "event_type": "database_session_error",
                "error": str(exc),
            }))
            raise
        finally:
            session.close()
