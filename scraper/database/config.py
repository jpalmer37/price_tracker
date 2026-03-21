import os


def get_database_url() -> str:
    """Build a PostgreSQL connection URL from environment variables."""
    user = os.environ["DATABASE_USERNAME"]
    password = os.environ["DATABASE_PASSWORD"]
    host = os.environ.get("DATABASE_HOST", "localhost")
    port = os.environ.get("DATABASE_PORT", "5432")
    db_name = os.environ.get("DATABASE_NAME", "price_tracker")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

