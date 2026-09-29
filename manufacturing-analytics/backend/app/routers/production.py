"""Production router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import production_service

router = APIRouter(prefix="/api/production", tags=["Production"])


@router.get("")
def list_production(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    plant_id: int | None = Query(None), machine_id: int | None = Query(None),
    product_id: int | None = Query(None), status: str | None = Query(None),
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    sort_by: str = Query("production_date"), sort_dir: str = Query("desc"),
    db: Session = Depends(get_db),
):
    return production_service.get_production_list(
        db, page, page_size, plant_id, machine_id, product_id, status,
        date_from, date_to, sort_by, sort_dir,
    )


@router.get("/by-plant")
def production_by_plant(
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return production_service.get_production_by_plant(db, date_from, date_to)
