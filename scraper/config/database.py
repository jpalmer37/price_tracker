import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    params = {
        "user": os.getenv("DATABASE_USERNAME"),
        "password": os.getenv("DATABASE_PASSWORD"),
        "host": os.getenv("DATABASE_HOST"),
        "port": os.getenv("DATABASE_PORT"),
        "db_name": os.getenv("DATABASE_NAME"),
    }

    missing = [key for key, value in params.items() if not value]
    if missing:
        raise ValueError(f"Missing database configuration values: {', '.join(sorted(missing))}")

    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**params)


def get_config():
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "user": os.getenv("DATABASE_USERNAME"),
        "password": os.getenv("DATABASE_PASSWORD"),
        "host": os.getenv("DATABASE_HOST"),
        "port": os.getenv("DATABASE_PORT"),
        "database": os.getenv("DATABASE_NAME"),
    }
