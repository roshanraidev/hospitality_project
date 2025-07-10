from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from backend.models import FoodRecord, WeekSubmission
from backend.database import get_db

router = APIRouter(prefix="/api", tags=["Food Records"])

# Pydantic models
class FoodRecordItem(BaseModel):
    date: str
    time: str
    desc: str
    temp1: str
    time2: str
    temp2: str
    action: str

class WeeklyRecord(BaseModel):
    week_id: int
    site_id: int
    data: List[FoodRecordItem]

@router.post("/save-weekly-record")
def save_weekly_record(record: WeeklyRecord, db: Session = Depends(get_db)):
    try:
        week = db.query(WeekSubmission).filter_by(id=record.week_id, site_id=record.site_id).first()
        if not week:
            raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

        db.query(FoodRecord).filter_by(week_id=record.week_id, site_id=record.site_id).delete()

        for item in record.data:
            db.add(FoodRecord(
                week_id=record.week_id,
                site_id=record.site_id,
                date=item.date,
                time=item.time,
                description=item.desc,
                temp1=item.temp1,
                time2=item.time2,
                temp2=item.temp2,
                action=item.action
            ))
        db.commit()
        return {"message": "Records saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-weekly-record/{week_id}")
def get_weekly_record(week_id: int, site_id: int, db: Session = Depends(get_db)):
    try:
        records = db.query(FoodRecord).filter_by(week_id=week_id, site_id=site_id).all()
        result = [
            {
                "date": r.date,
                "time": r.time,
                "desc": r.description,
                "temp1": r.temp1,
                "time2": r.time2,
                "temp2": r.temp2,
                "action": r.action
            } for r in records
        ]
        return {"week_id": week_id, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
