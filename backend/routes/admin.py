from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import SessionLocal
from backend.models import Recipe

router = APIRouter()

# ✅ Schema for creating a recipe (requires site_ids)
class RecipeSchema(BaseModel):
    site_ids: List[int]
    category: str
    dish: str
    ingredients: str
    method: str
    yield_: str
    shelfLife: str
    allergies: str
    image: str = ""

    class Config:
        orm_mode = True

# ✅ Schema for updating a recipe (no site_ids, all fields optional)
class RecipeUpdateSchema(BaseModel):
    category: Optional[str]
    dish: Optional[str]
    ingredients: Optional[str]
    method: Optional[str]
    yield_: Optional[str]
    shelfLife: Optional[str]
    allergies: Optional[str]
    image: Optional[str] = ""

    class Config:
        orm_mode = True

# ✅ DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get all recipes, optionally filter by site_id
@router.get("/")
def get_all(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    if site_id is not None:
        return db.query(Recipe).filter(Recipe.site_id == site_id).all()
    return db.query(Recipe).all()

# ✅ Create a recipe for multiple sites
@router.post("/")
def create(recipe: RecipeSchema, db: Session = Depends(get_db)):
    created = []
    for site_id in recipe.site_ids:
        db_recipe = Recipe(
            site_id=site_id,
            category=recipe.category,
            dish=recipe.dish,
            ingredients=recipe.ingredients,
            method=recipe.method,
            yield_=recipe.yield_,
            shelfLife=recipe.shelfLife,
            allergies=recipe.allergies,
            image=recipe.image
        )
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        created.append(db_recipe)
    return created

# ✅ Update a specific recipe using partial data (PATCH-like behavior)
@router.put("/{id}")
def update_recipe(id: int, recipe: RecipeUpdateSchema, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for key, value in recipe.dict(exclude_unset=True).items():
        setattr(db_recipe, key, value)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

# ✅ Delete a recipe by ID
@router.delete("/{id}")
def delete_recipe(id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted"}
