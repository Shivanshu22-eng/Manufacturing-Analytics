"""Orders router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("")
def list_orders(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    product_id: int | None = Query(None), status: str | None = Query(None),
    priority: str | None = Query(None), customer: str | None = Query(None),
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return order_service.get_orders(
        db, page, page_size, product_id, status, priority, customer, date_from, date_to,
    )
