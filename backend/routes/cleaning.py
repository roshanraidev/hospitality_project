from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List
from backend.models import CleaningSchedule
from backend.routes.schemas import CleaningScheduleCreate
from backend.database import get_db

router = APIRouter()

# ✅ Save cleaning schedule
@router.post("/cleaning-tasks")
def save_cleaning_schedule(
    items: List[CleaningScheduleCreate] = Body(...),  # ✅ Explicitly extract from request body
    db: Session = Depends(get_db)
):
    if not items:
        raise HTTPException(status_code=400, detail="No cleaning tasks provided")

    site_id = items[0].site_id
    week_id = items[0].week_id

    # ✅ Delete existing tasks for the same site and week
    db.query(CleaningSchedule).filter_by(site_id=site_id, week_id=week_id).delete()

    for item in items:
        task_data = item.dict()
        db.add(CleaningSchedule(**task_data))

    db.commit()
    return {"status": "success", "count": len(items)}

# ✅ Get cleaning schedule (admin = week_id 0)
@router.get("/cleaning-tasks")
def get_cleaning_schedule(
    site_id: int = Query(...),
    week_id: int = Query(0),  # Default 0 for admin
    db: Session = Depends(get_db)
):
    return db.query(CleaningSchedule).filter_by(site_id=site_id, week_id=week_id).all()

# ✅ Flat key-value version (for alternative frontend support)
@router.get("/cleaning/flat")
def get_cleaning_schedule_flat(
    site_id: int = Query(...),
    db: Session = Depends(get_db)
):
    items = db.query(CleaningSchedule).filter_by(site_id=site_id, week_id=0).all()

    if not items:
        return {"data": {}}

    flat_data = {}
    for idx, item in enumerate(items):
        flat_data[f"item_{idx}"] = item.item
        flat_data[f"chemical_{idx}"] = item.chemical
        flat_data[f"ppe_{idx}"] = item.ppe
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            flat_data[f"{day}_{idx}"] = getattr(item, day)

    return {"data": flat_data}
