from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Site, UserSite
from backend.utils import verify_password
from backend.auth import create_access_token

router = APIRouter()

@router.post("/login")
def login(credentials: dict, db: Session = Depends(get_db)):
    email = credentials.get("email")
    password = credentials.get("password")
    role = credentials.get("role")
    site_name = credentials.get("site")

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if role == "admin":
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Not an admin user")
        token_data = {"user_id": user.id, "is_admin": True}
        token = create_access_token(token_data)
        return {
            "access_token": token,
            "is_admin": True
        }

    if role == "user":
        if user.is_admin:
            raise HTTPException(status_code=403, detail="User is admin, select correct role")

        site = db.query(Site).filter(Site.name == site_name).first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")

        user_site = db.query(UserSite).filter_by(user_id=user.id, site_id=site.id).first()
        if not user_site:
            raise HTTPException(status_code=403, detail="User not assigned to this site")

        token_data = {
            "user_id": user.id,
            "is_admin": False,
            "site": site.name,
            "site_id": site.id  # ✅ Include site_id in token if needed
        }
        token = create_access_token(token_data)

        return {
            "access_token": token,
            "is_admin": False,
            "site": site.name,
            "site_id": site.id  # ✅ Pass site_id to frontend
        }
