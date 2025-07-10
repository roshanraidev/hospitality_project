from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Supplier, Unit
from .schemas import NameItem

router = APIRouter()

# --- SUPPLIERS ---

@router.get("/suppliers")
def get_suppliers(site_id: int = Query(...), db: Session = Depends(get_db)):
    return db.query(Supplier).filter_by(site_id=site_id).all()

@router.post("/suppliers")
def add_supplier(item: NameItem, site_id: int = Query(...), db: Session = Depends(get_db)):
    if db.query(Supplier).filter_by(name=item.name, site_id=site_id).first():
        raise HTTPException(status_code=400, detail="Supplier already exists")
    supplier = Supplier(name=item.name, site_id=site_id)
    db.add(supplier)
    db.commit()
    return supplier

@router.delete("/suppliers/{name}")
def delete_supplier(name: str, site_id: int = Query(...), db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter_by(name=name, site_id=site_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
    return {"message": "Deleted"}


# --- UNITS ---

@router.get("/units")
def get_units(site_id: int = Query(...), db: Session = Depends(get_db)):
    return db.query(Unit).filter_by(site_id=site_id).all()

@router.post("/units")
def add_unit(item: NameItem, site_id: int = Query(...), db: Session = Depends(get_db)):
    if db.query(Unit).filter_by(name=item.name, site_id=site_id).first():
        raise HTTPException(status_code=400, detail="Unit already exists")
    unit = Unit(name=item.name, site_id=site_id)
    db.add(unit)
    db.commit()
    return unit

@router.delete("/units/{name}")
def delete_unit(name: str, site_id: int = Query(...), db: Session = Depends(get_db)):
    unit = db.query(Unit).filter_by(name=name, site_id=site_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"message": "Deleted"}
