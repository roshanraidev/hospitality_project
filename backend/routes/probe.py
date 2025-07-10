from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ProbeRecord, WeekSubmission

router = APIRouter()

@router.post("/probe/submit")
async def save_probe_data(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    week_id = payload.get("week_id")
    site_id = payload.get("site_id")
    data = payload.get("data")

    if not week_id or not site_id or not data:
        raise HTTPException(status_code=400, detail="Missing 'week_id', 'site_id' or 'data'")

    week = db.query(WeekSubmission).filter_by(id=week_id, site_id=site_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Invalid week_id or site_id")

    # Delete existing records for this week and site
    db.query(ProbeRecord).filter_by(week_id=week_id, site_id=site_id).delete()

    for entry in data:
        record = ProbeRecord(
            week_id=week_id,
            site_id=site_id,
            date=entry["date"],
            probe_no=entry["probe_no"],
            temp_ice=int(entry["temp_ice"]),
            temp_water=int(entry["temp_water"]),
            signature=entry.get("signature", "")
        )
        db.add(record)

    db.commit()
    return {"message": "Data saved to database"}


@router.get("/probe/{week_id}")
def get_probe_data(week_id: int, site_id: int = Query(...), db: Session = Depends(get_db)):
    records = db.query(ProbeRecord).filter_by(week_id=week_id, site_id=site_id).all()
    return {
        "week_id": week_id,
        "site_id": site_id,
        "data": [
            {
                "id": r.id,
                "date": r.date,
                "probe_no": r.probe_no,
                "temp_ice": r.temp_ice,
                "temp_water": r.temp_water,
                "signature": r.signature,
            }
            for r in records
        ],
    }

@router.delete("/probe/{week_id}/{site_id}/{record_id}")
def delete_probe_record(week_id: int, site_id: int, record_id: int, db: Session = Depends(get_db)):
    db.query(ProbeRecord).filter_by(week_id=week_id, site_id=site_id, id=record_id).delete()
    db.commit()
    return {"message": "Deleted"}
