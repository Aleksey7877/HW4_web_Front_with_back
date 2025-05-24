from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from . import models, schemas, crud
from .kafka_producer import send_kafka_event
from .kafka_setup import create_kafka_topic
from .kafka_consumer import start_consumer
from threading import Thread
from .grpc_server import serve as start_grpc_server

app = FastAPI(title="Products Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    send_kafka_event("products", {"action": "warmup"})
    init_db()
    create_kafka_topic("products")
    start_consumer()
    Thread(target=start_grpc_server, daemon=True).start()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/products", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return [schemas.Product.from_orm(prod) for prod in crud.get_products(db, skip, limit)]

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return schemas.Product.from_orm(product)

@app.post("/products", response_model=schemas.Product, status_code=201)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        db_obj = crud.create_product(db, product_in)
        product_schema = schemas.Product.from_orm(db_obj)
        send_kafka_event("products", {'action': 'create', 'product': product_schema.dict()})
        return product_schema
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{product_id}", response_model=schemas.Product)
def replace_product(product_id: int, product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    updated = crud.update_product(db, product_id, schemas.ProductUpdate(**product_in.dict()))
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    product_schema = schemas.Product.from_orm(updated)
    send_kafka_event("products", {'action': 'update', 'product': product_schema.dict()})
    return product_schema

@app.patch("/products/{product_id}", response_model=schemas.Product)
def patch_product(product_id: int, product_in: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated = crud.update_product(db, product_id, product_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    product_schema = schemas.Product.from_orm(updated)
    send_kafka_event("products", {'action': 'update', 'product': product_schema.dict()})
    return product_schema

@app.patch("/products/{product_id}/decrease")
def decrease_quantity(product_id: int, payload: dict, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    amount = payload.get("amount", 1)
    product.available_quantity -= amount
    db.commit()
    return {"id": product_id, "new_quantity": product.available_quantity}

@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    send_kafka_event("products", {'action': 'delete', 'product_id': product_id})
    return schemas.Product.from_orm(deleted)