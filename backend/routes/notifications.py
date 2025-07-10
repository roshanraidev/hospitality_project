from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import NotificationStatus, Recipe, MonthlyAuditModel, MaintenanceLog, DailyReport, User, Site

router = APIRouter()

@router.get("/notifications", tags=["Notifications"])
def get_user_notifications(user_id: int, site_id: int, db: Session = Depends(get_db)):
    status = db.query(NotificationStatus).filter_by(user_id=user_id, site_id=site_id).first()

    if not status:
        return {
            "recipe": True,
            "inspection": True,
            "temp_records": True,
            "reports": True,
            "maintenance": True
        }

    recipe_updated = db.query(func.max(Recipe.updated_at)).filter_by(site_id=site_id).scalar()
    audit_updated = db.query(func.max(MonthlyAuditModel.date)).filter_by(site_id=site_id).scalar()
    temp_updated = db.query(func.max(DailyReport.created_at)).filter_by(site_id=site_id).scalar()
    report_updated = db.query(func.max(DailyReport.created_at)).filter_by(site_id=site_id).scalar()
    maintenance_updated = db.query(func.max(MaintenanceLog.date)).filter_by(site_id=site_id).scalar()

    return {
        "recipe": recipe_updated and (not status.last_seen_recipe or recipe_updated > status.last_seen_recipe),
        "inspection": audit_updated and (not status.last_seen_inspection or audit_updated > status.last_seen_inspection),
        "temp_records": temp_updated and (not status.last_seen_temp_records or temp_updated > status.last_seen_temp_records),
        "reports": report_updated and (not status.last_seen_reports or report_updated > status.last_seen_reports),
        "maintenance": maintenance_updated and (not status.last_seen_maintenance or maintenance_updated > status.last_seen_maintenance),
    }
