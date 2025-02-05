# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

class DatabaseConfig:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        # Create engine with connection pool
        self._engine = create_engine(
            self.connection_url,
            pool_size=5,        # Maximum number of persistent connections
            max_overflow=10,    # Maximum number of additional connections
            pool_timeout=30,    # Timeout waiting for connection (seconds)
            pool_recycle=1800,  # Recycle connections after 30 minutes
        )

        # Create session factory
        session_factory = sessionmaker(bind=self._engine)
        
        # Create thread-safe session factory
        self._session_factory = scoped_session(session_factory)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_factory(self):
        """Returns the session factory for dependency injection."""
        return self.get_session