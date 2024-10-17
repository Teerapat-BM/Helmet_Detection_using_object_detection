# api.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, HelmetCount
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI()

# เพิ่ม CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HelmetCountCreate(BaseModel):
    helmet_count: int
    no_helmet_count: int

class HelmetCountResponse(BaseModel):
    id: int
    helmet_count: int
    no_helmet_count: int
    timestamp: datetime

    class Config:
        orm_mode = True

# API endpoints
@app.post("/counts/", response_model=HelmetCountResponse)
def create_count(count: HelmetCountCreate, db: Session = Depends(get_db)):
    db_count = HelmetCount(
        helmet_count=count.helmet_count,
        no_helmet_count=count.no_helmet_count
    )
    db.add(db_count)
    db.commit()
    db.refresh(db_count)
    return db_count

@app.get("/counts/", response_model=List[HelmetCountResponse])
def get_counts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    counts = db.query(HelmetCount).offset(skip).limit(limit).all()
    return counts

@app.get("/latest/", response_model=HelmetCountResponse)
def get_latest_count(db: Session = Depends(get_db)):
    count = db.query(HelmetCount).order_by(HelmetCount.id.desc()).first()
    if count is None:
        raise HTTPException(status_code=404, detail="No counts found")
    return count