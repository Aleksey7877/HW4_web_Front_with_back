from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from . import models

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    models.Base.metadata.create_all(bind=engine)

    # 🔹 Инициализация базовых статусов заказа
    db = SessionLocal()
    try:
        if db.query(models.OrderStatus).count() == 0:
            default_statuses = [
                {"id": 1, "name": "new"},
                {"id": 2, "name": "processing"},
                {"id": 3, "name": "completed"},
                {"id": 4, "name": "canceled"},
            ]
            for status in default_statuses:
                db.add(models.OrderStatus(**status))
            db.commit()
    finally:
        db.close()
