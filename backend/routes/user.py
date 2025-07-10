from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Site, UserSite
from backend.utils import hash_password
from backend.routes.schemas import CreateUserSchema

router = APIRouter()

# ✅ Create new site
@router.post("/sites")
def create_site(name: str, db: Session = Depends(get_db)):
    existing = db.query(Site).filter(Site.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Site already exists")
    site = Site(name=name)
    db.add(site)
    db.commit()
    return {"message": "Site created"}

# ✅ Create user + assign sites
@router.post("/users")
def create_user(user_data: CreateUserSchema, db: Session = Depends(get_db)):
    email = user_data.email
    password = user_data.password
    site_names = user_data.site_names
    is_admin = user_data.is_admin  # <-- take is_admin from request

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(email=email, hashed_password=hash_password(password), is_admin=is_admin)
    db.add(user)
    db.commit()

    # Only assign sites if user is NOT admin
    if not is_admin:
        for site_name in site_names:
            site = db.query(Site).filter(Site.name == site_name.strip()).first()
            if not site:
                site = Site(name=site_name.strip())
                db.add(site)
                db.commit()

            user_site = UserSite(user_id=user.id, site_id=site.id)
            db.add(user_site)

    db.commit()
    return {"message": "✅ User created successfully"}

# ✅ Get all users
@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []

    for user in users:
        assigned_sites = [user_site.site.name for user_site in user.sites]
        result.append({
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "sites": assigned_sites
        })

    return result

# ✅ Get all sites
@router.get("/sites")
def get_sites(db: Session = Depends(get_db)):
    sites = db.query(Site).all()
    return [{"id": s.id, "name": s.name} for s in sites]


# ✅ Update user
@router.put("/users/{user_id}")
def update_user(user_id: int, user_data: CreateUserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = user_data.email

    if user_data.password:  # Only update password if provided
        user.hashed_password = hash_password(user_data.password)

    user.is_admin = user_data.is_admin  # <-- ✅ allow updating admin status

    # Clear existing site assignments
    db.query(UserSite).filter(UserSite.user_id == user.id).delete()

    # Only assign sites if NOT admin
    if not user.is_admin:
        for site_name in user_data.site_names:
            site = db.query(Site).filter(Site.name == site_name.strip()).first()
            if not site:
                site = Site(name=site_name.strip())
                db.add(site)
                db.commit()
            user_site = UserSite(user_id=user.id, site_id=site.id)
            db.add(user_site)

    db.commit()
    return {"message": "✅ User updated successfully"}

# ✅ Delete user
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(UserSite).filter(UserSite.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return {"message": "✅ User deleted successfully"}
