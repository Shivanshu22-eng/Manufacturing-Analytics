"""Machines router."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import machine_service

router = APIRouter(prefix="/api/machines", tags=["Machines"])


@router.get("")
def list_machines(
    plant_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return machine_service.get_machines(db, plant_id=plant_id, status=status)


@router.get("/downtime")
def machine_downtime(
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    plant_id: int | None = Query(None), top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return machine_service.get_machine_downtime(db, date_from, date_to, plant_id, top_n)


@router.get("/{machine_id}")
def machine_detail(machine_id: int, db: Session = Depends(get_db)):
    result = machine_service.get_machine_detail(db, machine_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")
    return result
