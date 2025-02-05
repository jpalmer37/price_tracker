from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Store(Base):
    __tablename__ = 'stores'
    primary_id = Column(Integer, primary_key=True)
    store_name = Column(String) 
    store_website = Column(String)

    items = relationship('Item', back_populates='stores')

    def __str__(self):
        return f"Store: {self.store_name} ({self.website})"
    