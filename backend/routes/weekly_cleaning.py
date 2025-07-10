from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import RootModel
from typing import List
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import WeeklyCleaningTask

router = APIRouter()

class TaskList(RootModel[List[str]]):  # List of plain task names
    pass

@router.post("/weekly-tasks")
def save_weekly_tasks(tasks: TaskList, site_id: int = Query(...), db: Session = Depends(get_db)):
    if not tasks.root:
        raise HTTPException(status_code=400, detail="No tasks provided.")

    try:
        # Remove existing tasks for this site
        db.query(WeeklyCleaningTask).filter_by(site_id=site_id).delete()

        for task_name in tasks.root:
            db.add(WeeklyCleaningTask(item=task_name, site_id=site_id))

        db.commit()
        return {"message": f"{len(tasks.root)} tasks saved for site {site_id}."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-tasks", response_model=List[str])
def get_weekly_tasks(site_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        return [task.item for task in db.query(WeeklyCleaningTask).filter_by(site_id=site_id).all()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
