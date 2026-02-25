import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    params = dict(user=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        db_name=os.getenv("DATABASE_NAME")
    )
    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**params)

def get_config():
    return {
        "user": os.getenv("DATABASE_USERNAME"),
        "password": os.getenv("DATABASE_PASSWORD"),
        "host": os.getenv("DATABASE_HOST"),
        "port": os.getenv("DATABASE_PORT"),
        "database": os.getenv("DATABASE_NAME")
    }
