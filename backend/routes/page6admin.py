from fastapi import APIRouter, HTTPException, Query
from backend.database import SessionLocal
from backend.models import AuditChecklist
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ChecklistItem(BaseModel):
    item: str

@router.get("/api/checklist", response_model=List[ChecklistItem])
def get_checklist(site_id: int = Query(...)):
    db = SessionLocal()
    items = db.query(AuditChecklist).filter_by(site_id=site_id).all()
    return [{"item": i.item} for i in items]

@router.post("/api/checklist")
def add_item(item: ChecklistItem, site_id: int = Query(...)):
    db = SessionLocal()
    if db.query(AuditChecklist).filter_by(item=item.item, site_id=site_id).first():
        raise HTTPException(status_code=400, detail="Item already exists")
    db_item = AuditChecklist(item=item.item, site_id=site_id)
    db.add(db_item)
    db.commit()
    return {"message": "Item added"}

@router.delete("/api/checklist/{item}")
def delete_item(item: str, site_id: int = Query(...)):
    db = SessionLocal()
    entry = db.query(AuditChecklist).filter_by(item=item, site_id=site_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(entry)
    db.commit()
    return {"message": "Item deleted"}
