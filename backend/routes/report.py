# backend/routes/daily_report.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import DailyReport
from backend.routes.schemas import DailyReportCreate, DailyReportResponse
from typing import List, Optional
router = APIRouter()

@router.post("/daily-report", response_model=DailyReportResponse)
def create_daily_report(payload: DailyReportCreate, db: Session = Depends(get_db)):
    report = DailyReport(**payload.dict())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/daily-report", response_model=List[DailyReportResponse])
def get_all_reports(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(DailyReport)
    if site_id:
        query = query.filter(DailyReport.site_id == site_id)
    return query.order_by(DailyReport.created_at.desc()).all()
