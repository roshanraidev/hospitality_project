from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import DailyReport, User
from backend.routes.schemas import DailyReportCreate, DailyReportResponse
from backend.auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/daily-report", response_model=DailyReportResponse)
def create_daily_report(
    payload: DailyReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Enforce site_id from token, not from client
    if not current_user.sites:
        raise HTTPException(status_code=403, detail="User is not assigned to any site.")

    site_id = current_user.sites[0].site_id  # Assuming one site per user
    report = DailyReport(
        site_id=site_id,
        date=payload.date,
        day=payload.day,
        report=payload.report
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/daily-report", response_model=List[DailyReportResponse])
def get_all_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.sites:
        raise HTTPException(status_code=403, detail="User is not assigned to any site.")

    site_id = current_user.sites[0].site_id
    return (
        db.query(DailyReport)
        .filter(DailyReport.site_id == site_id)
        .order_by(DailyReport.created_at.desc())
        .all()
    )
