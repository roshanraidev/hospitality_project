from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import (
    WeekSubmission, AuditSubmission, ProbeRecord, FoodRecord,
    DailyCleaningChecklist, KitchenLog, WeeklyAuditReport,
    AuditResponse, WeeklyCleaningTask  # ✅ Make sure all needed models are imported
)
import json

router = APIRouter()

# ✅ 1️⃣ Get weeks filtered by site_id
@router.get("/weeks")
def get_weeks(site_id: int = Query(...), db: Session = Depends(get_db)):
    weeks = db.query(WeekSubmission).filter(WeekSubmission.site_id == site_id).all()
    return [
        {
            "id": w.id,
            "week": w.week,
            "start_date": w.start_date.strftime("%Y-%m-%d"),
            "end_date": w.end_date.strftime("%Y-%m-%d"),
        }
        for w in weeks
    ]

# ✅ 2️⃣ Cleaning Schedule (Page 1)
@router.get("/weekly-cleaning")
def get_weekly_cleaning_from_audit(week_id: int = Query(...), site_id: int = Query(...), db: Session = Depends(get_db)):
    record = db.query(AuditSubmission).filter_by(week_id=week_id, site_id=site_id).first()
    if not record or not record.data:
        return []

    data = record.data
    results = []

    index = 0
    while f"item_{index}" in data:
        results.append({
            "item": data.get(f"item_{index}", ""),
            "chemical": data.get(f"chemical_{index}", ""),
            "ppe": data.get(f"ppe_{index}", ""),
            "mon": data.get(f"mon_{index}", False),
            "tue": data.get(f"tue_{index}", False),
            "wed": data.get(f"wed_{index}", False),
            "thu": data.get(f"thu_{index}", False),
            "fri": data.get(f"fri_{index}", False),
            "sat": data.get(f"sat_{index}", False),
            "sun": data.get(f"sun_{index}", False),
        })
        index += 1

    return results

# ✅ 3️⃣ Probe Records (Page 2)
@router.get("/probe")
def get_probe_records(week_id: int = Query(...), site_id: int = Query(...), db: Session = Depends(get_db)):
    records = db.query(ProbeRecord).filter_by(week_id=week_id, site_id=site_id).all()
    return [
        {
            "date": r.date,
            "probe_no": r.probe_no,
            "temp_ice": r.temp_ice,
            "temp_water": r.temp_water,
            
        }
        for r in records
    ]

# ✅ 4️⃣ Food Holding Records (Page 3)
@router.get("/food-records")
def get_food_records(week_id: int = Query(...), site_id: int = Query(...), db: Session = Depends(get_db)):
    records = db.query(FoodRecord).filter_by(week_id=week_id, site_id=site_id).all()
    return [
        {
            "date": r.date,
            "time": r.time,
            "description": r.description,
            "temp1": r.temp1,
            "time2": r.time2,
            "temp2": r.temp2,
            "action": r.action
        }
        for r in records
    ]

# ✅ 5️⃣ Daily Cleaning Checklist (Page 4)
@router.get("/cleaning-checklist")
def get_daily_cleaning_checklist(
    week_id: int = Query(...),
    site_id: int = Query(...),
    day: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(DailyCleaningChecklist).filter_by(week_id=week_id, site_id=site_id)
    if day:
        query = query.filter(DailyCleaningChecklist.day == day)
    records = query.all()

    tasks = db.query(WeeklyCleaningTask).filter_by(site_id=site_id).all()
    task_names = [t.item for t in tasks]

    return [
        {
            "day": r.day,
            "am_chef": r.am_chef,
            "pm_chef": r.pm_chef,
            "canvases": r.canvases,
            "tasks": task_names
        }
        for r in records
    ]

# ✅ 6️⃣ Kitchen Logs (Page 5)
@router.get("/kitchen-log")
def get_kitchen_log(
    week_id: int = Query(...),
    site_id: int = Query(...),
    date: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(KitchenLog).filter_by(week_id=week_id, site_id=site_id)
    if date:
        query = query.filter(KitchenLog.date == date)
    records = query.all()
    return [
        {
            "date": r.date,
            "delivery": json.loads(r.delivery or "[]"),
            "fridge": json.loads(r.fridge or "[]"),
            "cooking": json.loads(r.cooking or "[]"),
            "hot": json.loads(r.hot or "[]"),
            "cold": json.loads(r.cold or "[]"),
            "hot_water_temp": r.hot_water_temp,
            "rinse_temp": r.rinse_temp,
        }
        for r in records
    ]

# ✅ 7️⃣ Weekly Audit Report (Page 6)
@router.get("/audit-response")
def get_audit_response(
    week_id: int = Query(...),
    site_id: int = Query(...),
    db: Session = Depends(get_db)
):
    report = db.query(AuditResponse).filter_by(week_id=week_id, site_id=site_id).first()
    return {
        "data": report.data if report else {},
        "feedback": report.feedback if report else ""
        # Remove created_at unless you're sure the model has that column
        # "created_at": str(report.created_at) if hasattr(report, 'created_at') else ""
    }
