from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    product_quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    model_config = {"from_attributes": True}

class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    model_config = {"from_attributes": True}

class OrderStatus(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class OrderBase(BaseModel):
    customer_id: int
    address: Optional[str] = None
    information: Optional[str] = None
    status_id: Optional[int] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    number: Optional[str] = None
    customer_id: Optional[int] = None
    address: Optional[str] = None
    price: Optional[Decimal] = None
    status_id: Optional[int] = None
    information: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None

    class Config:
        model_config = {"from_attributes": True}

class Order(OrderBase):
    id: int
    number: str
    date: datetime
    price: Decimal
    customer: Customer
    items: List[OrderItem]
    status: OrderStatus
    model_config = {"from_attributes": True}
