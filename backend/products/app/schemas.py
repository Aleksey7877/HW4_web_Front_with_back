from pydantic import BaseModel, Field
from typing import Optional, Union
from decimal import Decimal
from enum import Enum

class ProductStatus(str, Enum):
    active = "active"
    archived = "archived"

class ProductBase(BaseModel):
    name: str = Field(..., example="Smartphone")
    description: Optional[str] = Field(None, example="Latest model with OLED")
    cost: Decimal = Field(..., example=499.99)
    status: ProductStatus = Field(ProductStatus.active)
    image_url: Optional[str] = None
    attributes: Optional[Union[dict, str]] = None


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    status: Optional[ProductStatus] = None
    image_url: Optional[str] = None
    attributes: Optional[Union[dict, str]] = None


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True
