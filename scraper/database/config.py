import os
from dotenv import load_dotenv

load_dotenv()

@staticmethod
def get_database_url():
    params = dict(user=os.getenv("DB_USER"),
				password=os.getenv("DB_PASSWORD"),
				host=os.getenv("DB_HOST"),
				port=os.getenv("DB_PORT"),
				db_name=os.getenv("DB_NAME")
    )
    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**params)

@staticmethod
def get_config():
    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME")
    }
