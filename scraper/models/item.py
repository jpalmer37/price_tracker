from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
class Item(Base):
    __tablename__ = 'items'
    primary_id = Column(Integer, primary_key=True)
    item_name = Column(String) 
    item_code = Column(String)
    item_url = Column(String)

    store_id = Column(Integer, ForeignKey('stores.primary_id'), nullable=False)
    store = relationship('Store', back_populates='items')

    price_snapshots = relationship('PriceSnapshot', back_populates='item')

    def __str__(self):
        return f"Store: {self.store_name} found at {self.website}"