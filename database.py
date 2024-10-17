# database.py
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# สร้าง SQLite Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./helmet_detection.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# สร้าง Model สำหรับเก็บข้อมูล
class HelmetCount(Base):
    __tablename__ = "helmet_counts"
    
    id = Column(Integer, primary_key=True, index=True)
    helmet_count = Column(Integer)
    no_helmet_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

# สร้างตารางในฐานข้อมูล
Base.metadata.create_all(bind=engine)

# Dependency สำหรับ FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()