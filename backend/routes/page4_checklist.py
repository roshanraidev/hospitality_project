from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import DailyCleaningChecklist, WeekSubmission, WeeklyCleaningTask
from typing import Dict
import traceback

router = APIRouter()


# ✅ Schema for incoming checklist data
class ChecklistSchema(BaseModel):
    week_id: int
    site_id: int
    day: str
    amChef: str
    pmChef: str
    canvases: Dict[str, str]


# ✅ Save or update checklist entry for a specific day
@router.post("/api/daily-cleaning-checklist")
def save_checklist(data: ChecklistSchema, db: Session = Depends(get_db)):
    try:
        # ✅ Ensure valid week-site combo
        week = db.query(WeekSubmission).filter_by(id=data.week_id, site_id=data.site_id).first()
        if not week:
            raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

        # ✅ Match entry by week + site + day
        existing = db.query(DailyCleaningChecklist).filter_by(
            week_id=data.week_id, site_id=data.site_id, day=data.day
        ).first()

        if existing:
            existing.am_chef = data.amChef
            existing.pm_chef = data.pmChef
            existing.canvases = data.canvases
        else:
            new_entry = DailyCleaningChecklist(
                week_id=data.week_id,
                site_id=data.site_id,
                day=data.day,
                am_chef=data.amChef,
                pm_chef=data.pmChef,
                canvases=data.canvases
            )
            db.add(new_entry)

        db.commit()
        return {"message": "Saved successfully"}

    except Exception:
        db.rollback()
        print("❌ Error in POST /api/daily-cleaning-checklist:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# ✅ Get checklist for a specific day
@router.get("/api/daily-cleaning-checklist/{week_id}")
def get_checklist(
    week_id: int,
    site_id: int = Query(...),
    day: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        entry = db.query(DailyCleaningChecklist).filter_by(
            week_id=week_id,
            site_id=site_id,
            day=day
        ).first()

        if entry:
            return {
                "day": entry.day,
                "amChef": entry.am_chef,
                "pmChef": entry.pm_chef,
                "canvases": entry.canvases
            }

        return {}

    except Exception:
        print("❌ Error in GET /api/daily-cleaning-checklist:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# ✅ Get cleaning tasks for site
@router.get("/api/cleaning-tasks")
def get_cleaning_tasks(site_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        tasks = db.query(WeeklyCleaningTask).filter_by(site_id=site_id).all()
        return [task.item for task in tasks]
    except Exception:
        print("❌ Error in GET /api/cleaning-tasks:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to fetch cleaning tasks")
