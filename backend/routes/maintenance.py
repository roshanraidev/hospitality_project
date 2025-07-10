from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import MaintenanceLog
from backend.routes.schemas import MaintenanceLogCreate, MaintenanceLogResponse

router = APIRouter()

@router.post("/maintenance-log", response_model=MaintenanceLogResponse)
def create_log(log: MaintenanceLogCreate, db: Session = Depends(get_db)):
    new_log = MaintenanceLog(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/maintenance-log", response_model=List[MaintenanceLogResponse])
def get_logs(site_id: int, db: Session = Depends(get_db)):
    return db.query(MaintenanceLog).filter(MaintenanceLog.site_id == site_id).order_by(MaintenanceLog.date.desc()).all()
