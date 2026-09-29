"""Maintenance router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import maintenance_service

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("")
def list_maintenance(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    plant_id: int | None = Query(None), machine_id: int | None = Query(None),
    maintenance_type: str | None = Query(None),
    is_completed: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    return maintenance_service.get_maintenance(
        db, page, page_size, plant_id, machine_id, maintenance_type, is_completed,
    )


@router.get("/overdue")
def overdue(db: Session = Depends(get_db)):
    return maintenance_service.get_overdue_maintenance(db)


@router.get("/upcoming")
def upcoming(db: Session = Depends(get_db)):
    return maintenance_service.get_upcoming_maintenance(db)
