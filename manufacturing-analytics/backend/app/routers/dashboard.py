"""Dashboard router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis")
def kpis(plant_id: int | None = Query(None), db: Session = Depends(get_db)):
    """Executive KPI summary card data."""
    return dashboard_service.get_kpis(db, plant_id=plant_id)


@router.get("/production-trend")
def production_trend(
    granularity: str = Query("monthly", enum=["daily", "weekly", "monthly"]),
    plant_id: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Production volume & efficiency trend."""
    return dashboard_service.get_production_trend(db, granularity, plant_id, date_from, date_to)
