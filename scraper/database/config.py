import os
from pathlib import Path


def get_database_url() -> str:
    """Build a SQLite connection URL from environment variables."""
    db_path = Path(os.environ.get("DATABASE_PATH", "price_tracker.db")).expanduser()
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"
