from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String)

    items = relationship("Item", back_populates="store")

    def __repr__(self) -> str:
        return f"<Store name={self.name!r}>"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    store = relationship("Store", back_populates="items")

    price_snapshots = relationship("PriceSnapshot", back_populates="item")

    def __repr__(self) -> str:
        return f"<Item name={self.name!r} url={self.url!r}>"


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    price = Column(Numeric(10, 2), nullable=True)

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    item = relationship("Item", back_populates="price_snapshots")

    def __repr__(self) -> str:
        return f"<PriceSnapshot item_id={self.item_id} price={self.price} ts={self.timestamp}>"
    


    
