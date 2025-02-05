from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class PriceSnapshot(Base):
    __tablename__ = 'price_snapshots'
    primary_id = Column(Integer, primary_key=True)

    date_time = Column(DateTime)
    price = Column(Float)

    item_id = Column(Integer, ForeignKey('items.primary_id'), nullable=False)
    item = relationship('Item', back_populates='price_snapshots')

    def __str__(self):
        return (f"PriceSnapshot: {self.item.item_name} at store {self.store.store_name} "
                f"on {self.date_time} for ${self.price}")
