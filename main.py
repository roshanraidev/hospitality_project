from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# ✅ Import routes
from backend.routes import (
    admin, cleaning, page1, probe, food_records, user, weekly_cleaning,
    page4_checklist, page5admin, page5, page6admin, page6, coverpage,
    view_routes, adminindex, report, maintenance, monthly_audit, login, notifications
)

# ✅ Database setup
from backend.database import Base, engine, SessionLocal
from backend.models import User
from backend.utils import hash_password

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routes
app.include_router(admin.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(cleaning.router, tags=["cleaning"])
app.include_router(page1.router, prefix="/audit", tags=["audit"])
app.include_router(probe.router, tags=["probe"])
app.include_router(food_records.router, tags=["food_records"])
app.include_router(weekly_cleaning.router, tags=["weekly_cleaning"])
app.include_router(page4_checklist.router, tags=["page4_checklist"])
app.include_router(page5admin.router, tags=["page5admin"])
app.include_router(page5.router, tags=["page5"])
app.include_router(page6admin.router, tags=["page6admin"])
app.include_router(page6.router, prefix="/api", tags=["page6"])
app.include_router(coverpage.router, tags=["coverpage"])
app.include_router(view_routes.router, prefix="/view", tags=["viewresult"])
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(maintenance.router, prefix="/api", tags=["maintenance"])
app.include_router(monthly_audit.router, prefix="/api/monthly", tags=["monthly_audit"])
app.include_router(login.router, prefix="/api", tags=["login"])
app.include_router(user.router, prefix="/api/adminindex", tags=["adminindex"])
app.include_router(adminindex.router, prefix="/api/adminindex", tags=["adminindex"])

# ✅ NEW: Notification system route
app.include_router(notifications.router, prefix="/api", tags=["notifications"])


# ✅ Redirect root to login.html
@app.get("/", include_in_schema=False)
def redirect_to_login():
    return RedirectResponse(url="/login.html")

# ✅ Mount frontend folder
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# ✅ Basic health check
@app.get("/api")
def read_root():
    return {"message": "Kitchen Audit API is running"}

# ✅ Create DB tables if not exist
Base.metadata.create_all(bind=engine)

# ✅ Create super admin if not exists
