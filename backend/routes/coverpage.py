from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import WeekSubmission
from backend.routes.schemas import WeekSubmissionSchema
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/coverpage", tags=["Coverpage"])

# ✅ Create or submit new week (site-specific)
@router.post("/submit", response_model=dict)
def submit_week(payload: WeekSubmissionSchema, db: Session = Depends(get_db)):
    try:
        start_date = datetime.strptime(payload.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(payload.end_date, "%Y-%m-%d").date()

        if not payload.site_id:
            raise HTTPException(status_code=400, detail="Missing site_id")

        # ✅ Prevent duplicate open week for the same site with same dates
        existing_week = db.query(WeekSubmission).filter_by(
            start_date=start_date,
            end_date=end_date,
            is_closed=False,
            site_id=payload.site_id
        ).first()

        if existing_week:
            return {"message": "Week already exists", "id": existing_week.id}

        new_entry = WeekSubmission(
            week=payload.week,
            start_date=start_date,
            end_date=end_date,
            site_id=payload.site_id,
            is_closed=False
        )

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {"message": "Week saved successfully", "id": new_entry.id}

    except Exception as e:
        db.rollback()
        print("❌ Error inserting week:", e)
        raise HTTPException(status_code=500, detail="Failed to save week")

# ✅ Return open week for a specific site
@router.get("/get-open-week", response_model=Optional[dict])
def get_open_week(site_id: int = Query(...), db: Session = Depends(get_db)):
    open_week = db.query(WeekSubmission).filter_by(
        is_closed=False,
        site_id=site_id
    ).order_by(WeekSubmission.id.desc()).first()

    if not open_week:
        return None

    return {
        "week_id": open_week.id,
        "week": open_week.week,
        "start_date": open_week.start_date.isoformat(),
        "end_date": open_week.end_date.isoformat()
    }

# ✅ Return specific week by ID (also checks site_id)
@router.get("/get-week/{week_id}", response_model=Optional[dict])
def get_week_by_id(week_id: int, site_id: int = Query(...), db: Session = Depends(get_db)):
    week = db.query(WeekSubmission).filter_by(
        id=week_id,
        is_closed=False,
        site_id=site_id
    ).first()

    if not week:
        return None

    return {
        "week_id": week.id,
        "week": week.week,
        "start_date": week.start_date.isoformat(),
        "end_date": week.end_date.isoformat()
    }
