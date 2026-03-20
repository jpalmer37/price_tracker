from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)

    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    store = relationship("Store", back_populates="items")

    price_snapshots = relationship("PriceSnapshot", back_populates="item", cascade="all, delete-orphan")

    def __str__(self):
        return f"Item: {self.name} found at {self.url}"


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    base_url = Column(String, nullable=False, unique=True)

    items = relationship("Item", back_populates="store", cascade="all, delete-orphan")

    def __str__(self):
        return f"Store: {self.name} ({self.base_url})"


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    primary_id = Column(Integer, primary_key=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    price = Column(Numeric(10, 2), nullable=True)

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    item = relationship("Item", back_populates="price_snapshots")

    def __str__(self):
        return (f"PriceSnapshot: {self.item.name} at store {self.item.store.name} "
                f"on {self.timestamp} for ${self.price}")
