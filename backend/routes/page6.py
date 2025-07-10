from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AuditResponse, WeekSubmission
from backend.routes.schemas import AuditResponseCreate
from datetime import date, timedelta

router = APIRouter()

# ✅ Save audit response
@router.post("/audit-response")
def submit_audit(response: AuditResponseCreate, db: Session = Depends(get_db)):
    week = db.query(WeekSubmission).filter_by(id=response.week_id, site_id=response.site_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

    db_entry = AuditResponse(
        week_id=response.week_id,
        site_id=response.site_id,
        data=response.data,
        feedback=response.feedback
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return {"message": "Audit response saved", "id": db_entry.id}

# ✅ ⬇️ NEW: Fetch saved audit response for readonly mode
@router.get("/audit-response")
def get_audit_response(week_id: int = Query(...), site_id: int = Query(...), db: Session = Depends(get_db)):
    entry = db.query(AuditResponse).filter_by(week_id=week_id, site_id=site_id).first()
    if not entry:
        return {"data": {}, "feedback": ""}
    return {
        "data": entry.data,
        "feedback": entry.feedback
    }

# ✅ Create a new week
@router.post("/create-week")
def create_new_week(site_id: int = Query(...), db: Session = Depends(get_db)):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    new_week = WeekSubmission(
        week=f"Week {start_of_week.strftime('%Y-%m-%d')}",
        start_date=start_of_week,
        end_date=end_of_week,
        is_closed=False,
        site_id=site_id
    )
    db.add(new_week)
    db.commit()
    db.refresh(new_week)
    return {"id": new_week.id}

# ✅ Finish (close) a week
@router.post("/finish-week/{week_id}")
def finish_week(week_id: int, site_id: int = Query(...), db: Session = Depends(get_db)):
    week = db.query(WeekSubmission).filter_by(id=week_id, site_id=site_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    if week.is_closed:
        raise HTTPException(status_code=400, detail="Week is already closed")

    week.is_closed = True
    db.commit()
    return {"message": "Week closed successfully"}
