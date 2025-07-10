from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Float, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime


class WeekSubmission(Base):
    __tablename__ = "week_submissions"

    id = Column(Integer, primary_key=True, index=True)
    week = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    category = Column(String, nullable=False)
    dish = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    method = Column(Text, nullable=False)
    yield_ = Column(String, nullable=False)
    shelfLife = Column(String, nullable=False)
    allergies = Column(Text, nullable=False)
    image = Column(Text)

    site = relationship("Site")


class CleaningSchedule(Base):
    __tablename__ = "cleaning_schedule"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    item = Column(String)
    chemical = Column(String)
    ppe = Column(String)
    mon = Column(Boolean, default=False)
    tue = Column(Boolean, default=False)
    wed = Column(Boolean, default=False)
    thu = Column(Boolean, default=False)
    fri = Column(Boolean, default=False)
    sat = Column(Boolean, default=False)
    sun = Column(Boolean, default=False)


class AuditSubmission(Base):
    __tablename__ = "audit_submissions"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    data = Column(JSON)


class ProbeRecord(Base):
    __tablename__ = "probe_records"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    date = Column(String)
    probe_no = Column(String)
    temp_ice = Column(Integer)
    temp_water = Column(Integer)
    signature = Column(String)


class FoodRecord(Base):
    __tablename__ = "food_records"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    date = Column(String)
    time = Column(String)
    description = Column(String)
    temp1 = Column(String)
    time2 = Column(String)
    temp2 = Column(String)
    action = Column(String)


class WeeklyCleaningTask(Base):
    __tablename__ = "weekly_cleaning_tasks"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)


class DailyCleaningChecklist(Base):
    __tablename__ = "daily_cleaning_checklist"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    day = Column(String)
    am_chef = Column(String)
    pm_chef = Column(String)
    canvases = Column(JSON)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("name", "site_id", name="uq_supplier_name_site"),)


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("name", "site_id", name="uq_unit_name_site"),)


class KitchenLog(Base):
    __tablename__ = "kitchen_logs"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    date = Column(String)

    delivery = Column(JSON)
    fridge = Column(JSON)
    cooking = Column(JSON)
    hot = Column(JSON)
    cold = Column(JSON)

    hot_water_temp = Column(Float)
    rinse_temp = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditChecklist(Base):
    __tablename__ = "audit_checklist"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("item", "site_id", name="uq_audit_checklist_item_site"),)


class WeeklyAuditReport(Base):
    __tablename__ = "weekly_audit_reports"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    checklist_data = Column(JSON, nullable=False)
    feedback = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditResponse(Base):
    __tablename__ = "audit_responses"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("week_submissions.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    data = Column(JSON, nullable=False)
    feedback = Column(Text)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    sites = relationship("UserSite", back_populates="user")


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("UserSite", back_populates="site")


class UserSite(Base):
    __tablename__ = "user_sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    user = relationship("User", back_populates="sites")
    site = relationship("Site", back_populates="users")

    __table_args__ = (UniqueConstraint('user_id', 'site_id'),)


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    date = Column(String, nullable=False)
    day = Column(String, nullable=False)
    report = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    issue = Column(String)
    priority = Column(String)
    status = Column(String)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)

    site = relationship("Site")


class MonthlyAuditModel(Base):
    __tablename__ = "monthly_audits"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    week_id = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    location = Column(String)
    chef_on_duty = Column(String)
    manager_on_duty = Column(String)
    data = Column(JSON)

    site = relationship("Site")


class NotificationStatus(Base):
    __tablename__ = "notification_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)

    last_seen_recipe = Column(DateTime)
    last_seen_inspection = Column(DateTime)
    last_seen_temp_records = Column(DateTime)
    last_seen_reports = Column(DateTime)
    last_seen_maintenance = Column(DateTime)

    user = relationship("User")
    site = relationship("Site")
