"""Quality router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import quality_service

router = APIRouter(prefix="/api/quality", tags=["Quality"])


@router.get("/inspections")
def inspections(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    plant_id: int | None = Query(None), machine_id: int | None = Query(None),
    product_id: int | None = Query(None), result: str | None = Query(None),
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return quality_service.get_inspections(
        db, page, page_size, plant_id, machine_id, product_id, result, date_from, date_to,
    )


@router.get("/defects")
def defects(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    plant_id: int | None = Query(None), product_id: int | None = Query(None),
    severity: str | None = Query(None), is_resolved: bool | None = Query(None),
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return quality_service.get_defects(
        db, page, page_size, plant_id, product_id, severity, is_resolved, date_from, date_to,
    )


@router.get("/defect-summary")
def defect_summary(
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return quality_service.get_defect_summary(db, date_from, date_to)


@router.get("/defect-trend")
def defect_trend(
    granularity: str = Query("monthly", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db),
):
    return quality_service.get_defect_trend(db, granularity)


@router.get("/top-defective-machines")
def top_defective_machines(top_n: int = Query(10, ge=1, le=20), db: Session = Depends(get_db)):
    return quality_service.get_top_defective_machines(db, top_n)
