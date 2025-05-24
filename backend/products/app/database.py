from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from . import models  

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    models.Base.metadata.create_all(bind=engine)
