from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import MaintenanceLog, User
from backend.routes.schemas import MaintenanceLogCreate, MaintenanceLogResponse
from backend.auth import get_current_user

router = APIRouter()

@router.post("/maintenance-log", response_model=MaintenanceLogResponse)
def create_log(
    log: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.sites:
        raise HTTPException(status_code=403, detail="User is not assigned to any site.")

    site_id = current_user.sites[0].site_id
    new_log = MaintenanceLog(
        site_id=site_id,
        date=log.date,
        issue=log.issue,
        priority=log.priority,
        status=log.status
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/maintenance-log", response_model=List[MaintenanceLogResponse])
def get_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.sites:
        raise HTTPException(status_code=403, detail="User is not assigned to any site.")

    site_id = current_user.sites[0].site_id
    return (
        db.query(MaintenanceLog)
        .filter(MaintenanceLog.site_id == site_id)
        .order_by(MaintenanceLog.date.desc())
        .all()
    )
