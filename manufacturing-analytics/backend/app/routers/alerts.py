"""Alerts router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("")
def get_alerts(db: Session = Depends(get_db)):
    """Return all active business-rule alerts, sorted by severity."""
    return alert_service.get_alerts(db)
