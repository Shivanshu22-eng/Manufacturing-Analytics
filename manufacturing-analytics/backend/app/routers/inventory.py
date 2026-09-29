"""Inventory router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/status")
def inventory_status(db: Session = Depends(get_db)):
    return inventory_service.get_inventory_status(db)


@router.get("")
def transactions(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    product_id: int | None = Query(None),
    transaction_type: str | None = Query(None),
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return inventory_service.get_inventory_transactions(
        db, page, page_size, product_id, transaction_type, date_from, date_to,
    )


@router.get("/trend")
def inventory_trend(
    granularity: str = Query("monthly", enum=["daily", "weekly", "monthly"]),
    db: Session = Depends(get_db),
):
    return inventory_service.get_inventory_trend(db, granularity)
