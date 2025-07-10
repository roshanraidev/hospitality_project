from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime
from datetime import date


# ✅ Week Submission (master week table)
class WeekSubmissionSchema(BaseModel):
    week: str
    start_date: str  # ISO string format
    end_date: str
    site_id: int  # ✅ Site linkage


# ✅ Cleaning Schedule
class CleaningScheduleCreate(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    item: str
    chemical: Optional[str] = ""
    ppe: Optional[str] = ""
    mon: Optional[bool] = False
    tue: Optional[bool] = False
    wed: Optional[bool] = False
    thu: Optional[bool] = False
    fri: Optional[bool] = False
    sat: Optional[bool] = False
    sun: Optional[bool] = False


# ✅ Probe Records
class ProbeEntry(BaseModel):
    date: str
    probe_no: str
    temp_ice: int
    temp_water: int
    signature: Optional[str]


class ProbeDataSubmission(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    data: List[ProbeEntry]


# ✅ Food Records
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
    site_id: int  # ✅ Site linkage
    data: List[FoodRecordItem]


# ✅ Daily Cleaning Checklist
class ChecklistSchema(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    day: str
    amChef: str
    pmChef: str
    canvases: dict


# ✅ Audit Submission
class AuditSubmissionCreate(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    data: Dict[str, Union[str, bool]]


# ✅ Audit Response
class AuditResponseCreate(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    data: Dict[str, str]
    feedback: Optional[str]


# ✅ Kitchen Logs
class DeliveryEntry(BaseModel):
    supplier: str
    food_checked: str = Field(..., alias="foodChecked")
    temperature: float
   

class FridgeEntry(BaseModel):
    unit: str
    am_temp: float = Field(..., alias="amTemp")
    pm_temp: float = Field(..., alias="pmTemp")


class CookingEntry(BaseModel):
    food: str
    time: str
    temp: float


class HotEntry(CookingEntry):
    pass


class ColdEntry(BaseModel):
    food: str
    time: str
    temp: float
   


class KitchenLogCreate(BaseModel):
    week_id: int
    site_id: int  # ✅ Site linkage
    id: Optional[int] = None
    date: str
    delivery: List[DeliveryEntry]
    fridge: List[FridgeEntry]
    cooking: List[CookingEntry]
    hot: List[HotEntry]
    cold: List[ColdEntry]
    hot_water_temp: Optional[float]
   
    rinse_temp: Optional[float]
   

    class Config:
        allow_population_by_field_name = True


# ✅ Supplier / Unit helper schemas
class NameItem(BaseModel):
    name: str
 

# ✅ User Creation
class CreateUserSchema(BaseModel):
    email: str
    password: str
    site_names: List[str]
    is_admin: bool = False


# schemas.py

class DailyReportCreate(BaseModel):
    site_id: int
    date: str
    day: str
    report: str

class DailyReportResponse(BaseModel):
    id: int
    site_id: int
    date: str
    day: str
    report: str
    created_at: datetime

    class Config:
        orm_mode = True



class MaintenanceLogCreate(BaseModel):
    date: date
    issue: str
    priority: str
    status: str
    site_id: int

class MaintenanceLogResponse(MaintenanceLogCreate):
    id: int

    class Config:
        orm_mode = True

# ✅ Monthly Audit Form Submission (from dynamic frontend)
class MonthlyAuditRow(BaseModel):
    col1: str
    col2: bool
    col3: str
    col4: str

class MonthlyAuditGroup(BaseModel):
    title: str
    rows: List[MonthlyAuditRow]

class MonthlyAuditSubmission(BaseModel):
    site_id: int
    week_id: int
    date: str
    location: str
    chef_on_duty: str
    manager_on_duty: str
    groups: List[MonthlyAuditGroup]
