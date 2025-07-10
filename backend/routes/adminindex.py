from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.models import WeekSubmission
from backend.database import get_db

router = APIRouter()

@router.get("/latest-week")
def get_latest_week(site_id: int = Query(...), db: Session = Depends(get_db)):
    latest = (
        db.query(WeekSubmission)
        .filter(WeekSubmission.site_id == site_id)
        .order_by(WeekSubmission.start_date.desc())
        .first()
    )
    if not latest:
        raise HTTPException(status_code=404, detail="No week found for this site.")
    return {"week_id": latest.id}
