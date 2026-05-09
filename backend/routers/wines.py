from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Wine])
def list_wines(
    skip: int = 0,
    limit: int = 100,
    varietal: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Wine)
    if varietal:
        query = query.filter(models.Wine.varietal.ilike(f"%{varietal}%"))
    if region:
        query = query.filter(models.Wine.region.ilike(f"%{region}%"))
    return query.order_by(models.Wine.date_tried.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Wine, status_code=201)
def create_wine(wine: schemas.WineCreate, db: Session = Depends(get_db)):
    db_wine = models.Wine(**wine.model_dump())
    db.add(db_wine)
    db.commit()
    db.refresh(db_wine)
    return db_wine


@router.get("/{wine_id}", response_model=schemas.Wine)
def get_wine(wine_id: int, db: Session = Depends(get_db)):
    wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    return wine


@router.patch("/{wine_id}", response_model=schemas.Wine)
def update_wine(
    wine_id: int, wine_update: schemas.WineUpdate, db: Session = Depends(get_db)
):
    wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    for field, value in wine_update.model_dump(exclude_unset=True).items():
        setattr(wine, field, value)
    db.commit()
    db.refresh(wine)
    return wine


@router.delete("/{wine_id}", status_code=204)
def delete_wine(wine_id: int, db: Session = Depends(get_db)):
    wine = db.query(models.Wine).filter(models.Wine.id == wine_id).first()
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    db.delete(wine)
    db.commit()
