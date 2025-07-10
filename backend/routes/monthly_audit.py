from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from backend.database import get_db
from backend.models import MonthlyAuditModel
from backend.routes.schemas import MonthlyAuditSubmission

router = APIRouter()


@router.post("/submit_monthly_audit", tags=["Monthly Audit"])
def submit_monthly_audit(payload: MonthlyAuditSubmission, db: Session = Depends(get_db)):
    try:
        audit_record = MonthlyAuditModel(
            site_id=payload.site_id,
            week_id=payload.week_id,
            date=payload.date,
            location=payload.location,
            chef_on_duty=payload.chef_on_duty,
            manager_on_duty=payload.manager_on_duty,
            data=[group.dict() for group in payload.groups]
        )
        db.add(audit_record)
        db.commit()
        db.refresh(audit_record)
        return {
            "message": "Monthly audit submitted successfully",
            "audit_id": audit_record.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit audit: {str(e)}")


@router.get("/monthly_audits", tags=["Monthly Audit"])
def get_monthly_audits(
    site_id: Optional[int] = Query(None, description="Filter by site ID"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(MonthlyAuditModel).options(joinedload(MonthlyAuditModel.site))
        if site_id is not None:
            query = query.filter(MonthlyAuditModel.site_id == site_id)

        audits = query.order_by(MonthlyAuditModel.date.desc()).all()

        return [
            {
                "id": audit.id,
                "site_id": audit.site_id,
                "site_name": audit.site.name if audit.site else None,  # ✅ Add site name
                "week_id": audit.week_id,
                "date": audit.date,
                "location": audit.location,
                "chef_on_duty": audit.chef_on_duty,
                "manager_on_duty": audit.manager_on_duty,
                "groups": audit.data
            }
            for audit in audits
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audits: {str(e)}")
