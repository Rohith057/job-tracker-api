from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=schemas.ApplicationOut)
def create_application(
    app_data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    new_app = models.Application(**app_data.dict(), owner_id=current_user.id)
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


@router.get("/", response_model=List[schemas.ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    company_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Application).filter(models.Application.owner_id == current_user.id)
    if status:
        query = query.filter(models.Application.status == status)
    if company_name:
        query = query.filter(models.Application.company_name.ilike(f"%{company_name}%"))
    return query.all()


@router.get("/{app_id}", response_model=schemas.ApplicationOut)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    app_obj = db.query(models.Application).filter(
        models.Application.id == app_id, models.Application.owner_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@router.put("/{app_id}", response_model=schemas.ApplicationOut)
def update_application(
    app_id: int,
    updates: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    app_obj = db.query(models.Application).filter(
        models.Application.id == app_id, models.Application.owner_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(app_obj, field, value)

    db.commit()
    db.refresh(app_obj)
    return app_obj


@router.delete("/{app_id}")
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    app_obj = db.query(models.Application).filter(
        models.Application.id == app_id, models.Application.owner_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app_obj)
    db.commit()
    return {"detail": "Application deleted successfully"}