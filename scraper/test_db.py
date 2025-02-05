#%%
import os 
import pandas as pd 
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

#%%
url = URL.create(
    drivername="postgresql",
    username="dbuser",
    host="localhost",
    database="price_tracker",
	password='S3cret',
	port=5432
)

engine = create_engine(url)
#%%
print("Connecting to Database...")
connection = engine.connect()

#%%
print("Setting Up Base... ")
Base = declarative_base()
#%%
print("Defining Table Classes...")
class PriceSnapshot(Base):
    __tablename__ = 'pricesnapshot'

    primary_id = Column(Integer, primary_key=True)
    item_id = Column(String)
    store_name = Column(String)
    item_name = Column(String)
    date_time = Column(DateTime)
    price = Column(Float)


#%% create engine
Base.metadata.create_all(engine)

#%% create a session
Session = sessionmaker(bind=engine)
session = Session()

#%%
current_datetime = datetime.now()

print(current_datetime)

data = {
    'item_id': "5390315",
    "store_name":"Costco",
    'item_name':'Zavida Organica Dark Coffee, 2 x 907 g',
    'date_time': current_datetime, 
    'price': 46.99
}

# Add the new user to the session
session.add(PriceSnapshot(**data))

data = {
    'item_id': "1694709",
    "store_name":"Costco",
    'item_name':'LEANFIT Whey Protein – Vanilla Flavour',
    'date_time': current_datetime, 
    'price': 59.99
}

# Add the new user to the session
session.add(PriceSnapshot(**data))

# Commit the session to write the objects to the database.
session.commit()
# %%
snapshots = session.query(PriceSnapshot).all()

for ss in snapshots:
    print(ss.item_name)
# %%

