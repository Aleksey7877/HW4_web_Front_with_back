from sqlalchemy import Column, Integer, String, Text, Numeric, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class ProductStatus(str, enum.Enum):
    active = "active"
    archived = "archived"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(ProductStatus), default=ProductStatus.active)
    image_url = Column(String(500), nullable=True)
    attributes = Column(JSON, nullable=True)

