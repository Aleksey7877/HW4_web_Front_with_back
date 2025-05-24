import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas


PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://products:8001/products")

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def create_order(db: Session, order: schemas.OrderCreate):
    customer = get_customer(db, order.customer_id)
    if not customer:
        raise ValueError("Customer not found")

    total_price = 0

    for item in order.items:
        response = requests.get(f"{PRODUCTS_SERVICE_URL}/{item.product_id}")
        if response.status_code != 200:
            raise ValueError(f"Product ID {item.product_id} not found in product service")

        product_data = response.json()
        total_price += float(product_data["cost"]) * item.product_quantity

    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    order_number = f"ORD-{now}"
    status_id = order.status_id if getattr(order, "status_id", None) else 1

    db_order = models.Order(
        number=order_number,
        customer_id=order.customer_id,
        address=order.address,
        price=total_price,
        status_id=status_id,
        information=order.information
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_quantity=item.product_quantity
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_obj = models.Customer(**customer.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()



def update_customer(db: Session, customer_id: int, customer_in: schemas.CustomerCreate):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        return None
    for field, value in customer_in.dict().items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order(db: Session, order_id: int, order_in: schemas.OrderUpdate):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None

    for field, value in order_in.dict(exclude_unset=True, exclude={"items"}).items():
        setattr(order, field, value)

    # если переданы новые items — пересчитать
    if hasattr(order_in, "items") and order_in.items:
        db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete()
        total_price = 0
        for item in order_in.items:
            response = requests.get(f"{PRODUCTS_SERVICE_URL}/{item.product_id}")
            if response.status_code != 200:
                raise ValueError(f"Product ID {item.product_id} not found in product service")
            product_data = response.json()
            cost = float(product_data["cost"])
            total_price += cost * item.product_quantity
            db_item = models.OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_quantity=item.product_quantity
            )
            db.add(db_item)
        order.price = total_price

    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    db.delete(order)
    db.commit()
    return order
