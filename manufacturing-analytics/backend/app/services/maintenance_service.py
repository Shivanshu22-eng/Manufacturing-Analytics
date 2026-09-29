"""Maintenance service."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import MaintenanceOut


def get_maintenance(
    db: Session,
    page: int = 1, page_size: int = 50,
    plant_id: int | None = None,
    machine_id: int | None = None,
    maintenance_type: str | None = None,
    is_completed: bool | None = None,
):
    where, params = ["1=1"], {}
    if plant_id:        where.append("mt.plant_id = :plant_id");       params["plant_id"]        = plant_id
    if machine_id:      where.append("mt.machine_id = :machine_id");   params["machine_id"]      = machine_id
    if maintenance_type:where.append("mt.maintenance_type = :mtype");  params["mtype"]           = maintenance_type
    if is_completed is not None: where.append("mt.is_completed = :ic");params["ic"]              = is_completed
    cond = " AND ".join(where)
    total  = db.execute(text(f"SELECT COUNT(*) FROM maintenance mt WHERE {cond}"), params).scalar()
    offset = (page - 1) * page_size
    sql = f"""
        SELECT mt.maintenance_id, mt.machine_id, m.machine_name,
               mt.plant_id, pl.plant_name,
               mt.maintenance_type, mt.description, mt.technician_name,
               mt.start_datetime, mt.end_datetime, mt.duration_hours,
               mt.cost, mt.is_completed, mt.parts_replaced
        FROM maintenance mt
        JOIN machines m  ON m.machine_id  = mt.machine_id
        JOIN plants   pl ON pl.plant_id   = mt.plant_id
        WHERE {cond}
        ORDER BY mt.start_datetime DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size; params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [MaintenanceOut(**dict(r)) for r in rows]}


def get_overdue_maintenance(db: Session):
    sql = """
        SELECT mt.maintenance_id, mt.machine_id, m.machine_name,
               mt.plant_id, pl.plant_name,
               mt.maintenance_type, mt.description, mt.technician_name,
               mt.start_datetime, mt.end_datetime, mt.duration_hours,
               mt.cost, mt.is_completed, mt.parts_replaced
        FROM maintenance mt
        JOIN machines m  ON m.machine_id = mt.machine_id
        JOIN plants   pl ON pl.plant_id  = mt.plant_id
        WHERE NOT mt.is_completed AND mt.start_datetime < NOW()
        ORDER BY mt.start_datetime ASC
        LIMIT 100
    """
    rows = db.execute(text(sql)).mappings().all()
    return [MaintenanceOut(**dict(r)) for r in rows]


def get_upcoming_maintenance(db: Session):
    sql = """
        SELECT mt.maintenance_id, mt.machine_id, m.machine_name,
               mt.plant_id, pl.plant_name,
               mt.maintenance_type, mt.description, mt.technician_name,
               mt.start_datetime, mt.end_datetime, mt.duration_hours,
               mt.cost, mt.is_completed, mt.parts_replaced
        FROM maintenance mt
        JOIN machines m  ON m.machine_id = mt.machine_id
        JOIN plants   pl ON pl.plant_id  = mt.plant_id
        WHERE NOT mt.is_completed
          AND mt.start_datetime >= NOW()
          AND mt.start_datetime <= NOW() + INTERVAL '30 days'
        ORDER BY mt.start_datetime ASC
        LIMIT 50
    """
    rows = db.execute(text(sql)).mappings().all()
    return [MaintenanceOut(**dict(r)) for r in rows]
