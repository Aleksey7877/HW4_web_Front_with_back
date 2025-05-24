import json
from sqlalchemy.orm import Session
from . import models, schemas


def get_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product and isinstance(product.attributes, str):
        try:
            product.attributes = json.loads(product.attributes)
        except Exception:
            pass
    return product

def get_products(db: Session, skip: int = 0, limit: int = 100):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    for p in products:
        if isinstance(p.attributes, str):
            try:
                p.attributes = json.loads(p.attributes)
            except Exception:
                pass
    return products


def create_product(db: Session, product: schemas.ProductCreate):
    data = product.dict()
    if data.get("attributes") and isinstance(data["attributes"], dict):
        data["attributes"] = json.dumps(data["attributes"]) 
    db_obj = models.Product(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_product(db: Session, product_id: int, updates: schemas.ProductUpdate):
    db_obj = get_product(db, product_id)
    updates_data = updates.dict(exclude_unset=True)
    if "attributes" in updates_data and isinstance(updates_data["attributes"], dict):
        updates_data["attributes"] = json.dumps(updates_data["attributes"])
    for field, value in updates_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_product(db: Session, product_id: int):
    db_obj = get_product(db, product_id)
    if not db_obj:
        return None
    db.delete(db_obj)
    db.commit()
    return db_obj