from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import KitchenLog, Supplier, Unit, WeekSubmission
from backend.routes.schemas import KitchenLogCreate
import json

router = APIRouter()

@router.get("/api/page5/dropdown")
def get_dropdown_data(site_id: int = Query(...), db: Session = Depends(get_db)):
    suppliers = [s.name for s in db.query(Supplier).filter_by(site_id=site_id).all()]
    units = [u.name for u in db.query(Unit).filter_by(site_id=site_id).all()]
    return {"suppliers": suppliers, "units": units}


@router.post("/api/page5/save")
def save_kitchen_log(entry: KitchenLogCreate, db: Session = Depends(get_db)):
    week = db.query(WeekSubmission).filter_by(id=entry.week_id, site_id=entry.site_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

    if entry.id:
        existing_log = db.query(KitchenLog).filter(
            KitchenLog.id == entry.id,
            KitchenLog.site_id == entry.site_id
        ).first()
    else:
        existing_log = db.query(KitchenLog).filter(
            KitchenLog.date == entry.date,
            KitchenLog.week_id == entry.week_id,
            KitchenLog.site_id == entry.site_id
        ).first()

    if existing_log:
        existing_log.delivery = json.dumps([e.dict(by_alias=True) for e in entry.delivery])
        existing_log.fridge = json.dumps([e.dict(by_alias=True) for e in entry.fridge])
        existing_log.cooking = json.dumps([e.dict(by_alias=True) for e in entry.cooking])
        existing_log.hot = json.dumps([e.dict(by_alias=True) for e in entry.hot])
        existing_log.cold = json.dumps([e.dict(by_alias=True) for e in entry.cold])
        existing_log.hot_water_temp = entry.hot_water_temp
        existing_log.rinse_temp = entry.rinse_temp
        db.commit()
        return {"status": "updated", "id": existing_log.id}
    else:
        new_log = KitchenLog(
            week_id=entry.week_id,
            site_id=entry.site_id,
            date=entry.date,
            delivery=json.dumps([e.dict(by_alias=True) for e in entry.delivery]),
            fridge=json.dumps([e.dict(by_alias=True) for e in entry.fridge]),
            cooking=json.dumps([e.dict(by_alias=True) for e in entry.cooking]),
            hot=json.dumps([e.dict(by_alias=True) for e in entry.hot]),
            cold=json.dumps([e.dict(by_alias=True) for e in entry.cold]),
            hot_water_temp=entry.hot_water_temp,
            rinse_temp=entry.rinse_temp
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return {"status": "created", "id": new_log.id}


@router.get("/api/page5/log/{log_date}")
def get_log_by_date(
    log_date: str,
    site_id: int = Query(...),
    week_id: int = Query(...),  # ✅ Added week_id as query param
    db: Session = Depends(get_db)
):
    log = db.query(KitchenLog).filter(
        KitchenLog.date == log_date,
        KitchenLog.site_id == site_id,
        KitchenLog.week_id == week_id     # ✅ Ensure match is scoped to the correct week
    ).first()
    if log:
        return {"id": log.id}
    return {}


@router.get("/api/page5/kitchen-log")
def get_kitchen_logs(week_id: int = Query(...), site_id: int = Query(...), db: Session = Depends(get_db)):
    logs = db.query(KitchenLog).filter_by(week_id=week_id, site_id=site_id).order_by(KitchenLog.date).all()
    return [
        {
            "date": log.date,
            "delivery": json.loads(log.delivery or "[]"),
            "fridge": json.loads(log.fridge or "[]"),
            "cooking": json.loads(log.cooking or "[]"),
            "hot": json.loads(log.hot or "[]"),
            "cold": json.loads(log.cold or "[]"),
            "hot_water_temp": log.hot_water_temp,
            "rinse_temp": log.rinse_temp
        }
        for log in logs
    ]
