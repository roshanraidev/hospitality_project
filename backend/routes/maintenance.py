from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import MaintenanceLog
from backend.routes.schemas import MaintenanceLogCreate, MaintenanceLogResponse

router = APIRouter()


@router.post("/maintenance-log", response_model=MaintenanceLogResponse)
def create_log(
    log: MaintenanceLogCreate,
    db: Session = Depends(get_db)
):
    if not log.site_id:
        raise HTTPException(status_code=400, detail="site_id is required")

    new_log = MaintenanceLog(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/maintenance-log", response_model=List[MaintenanceLogResponse])
def get_logs(
    site_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if not site_id:
        raise HTTPException(status_code=400, detail="Missing site_id in query")

    return (
        db.query(MaintenanceLog)
        .filter(MaintenanceLog.site_id == site_id)
        .order_by(MaintenanceLog.date.desc())
        .all()
    )


# ✅ Schema for updating status via JSON body
class StatusUpdate(BaseModel):
    status: str


# ✅ PATCH route using JSON body
@router.patch("/maintenance-log/{log_id}", response_model=MaintenanceLogResponse)
def update_log_status(
    log_id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db)
):
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    log.status = update.status
    db.commit()
    db.refresh(log)
    return log
