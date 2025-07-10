from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Union
from backend.database import get_db
from backend.models import AuditSubmission, CleaningSchedule, WeekSubmission

router = APIRouter()

class AuditSubmissionCreate(BaseModel):
    week_id: int
    site_id: int
    data: Dict[str, Union[str, bool]]

# ✅ Save or update audit submission
@router.post("/submit")
def submit_audit(payload: AuditSubmissionCreate, db: Session = Depends(get_db)):
    week = db.query(WeekSubmission).filter_by(id=payload.week_id, site_id=payload.site_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

    # 🛠 Upsert logic instead of delete/insert
    existing = db.query(AuditSubmission).filter_by(
        week_id=payload.week_id,
        site_id=payload.site_id
    ).first()

    if existing:
        existing.data = payload.data
    else:
        new_entry = AuditSubmission(
            week_id=payload.week_id,
            site_id=payload.site_id,
            data=payload.data
        )
        db.add(new_entry)

    db.commit()
    return {"status": "success"}

# ✅ Retrieve existing audit data for a week/site
@router.get("/record/{week_id}")
def get_submission_by_week(week_id: int, site_id: int = Query(...), db: Session = Depends(get_db)):
    record = db.query(AuditSubmission).filter_by(week_id=week_id, site_id=site_id).first()
    if not record:
        return {"data": {}}
    return {
        "week_id": record.week_id,
        "site_id": record.site_id,
        "data": record.data
    }

# ✅ Return site-specific cleaning tasks only
@router.get("/cleaning-tasks")
def get_cleaning_tasks(site_id: int = Query(...), db: Session = Depends(get_db)):
    tasks = db.query(CleaningSchedule).filter_by(site_id=site_id).all()
    return [
        {"item": t.item, "chemical": t.chemical, "ppe": t.ppe}
        for t in tasks
    ]
