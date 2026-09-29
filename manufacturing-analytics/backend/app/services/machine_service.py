"""Machine service."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import MachineOut, MachineDetailOut


def get_machines(db: Session, plant_id: int | None = None, status: str | None = None):
    where, params = ["1=1"], {}
    if plant_id: where.append("m.plant_id = :plant_id"); params["plant_id"] = plant_id
    if status:   where.append("m.status = :status");     params["status"]   = status
    sql = f"""
        SELECT m.machine_id, m.machine_name, m.machine_type, m.plant_id,
               pl.plant_name, m.model_number, m.manufacturer,
               m.installation_date, m.last_maintenance_date,
               m.status, m.hourly_capacity
        FROM machines m JOIN plants pl ON pl.plant_id = m.plant_id
        WHERE {' AND '.join(where)}
        ORDER BY m.machine_id
    """
    rows = db.execute(text(sql), params).mappings().all()
    return [MachineOut(**dict(r)) for r in rows]


def get_machine_detail(db: Session, machine_id: int) -> MachineDetailOut | None:
    sql = """
        SELECT m.machine_id, m.machine_name, m.machine_type, m.plant_id,
               pl.plant_name, m.model_number, m.manufacturer,
               m.installation_date, m.last_maintenance_date,
               m.status, m.hourly_capacity,
               v.total_shifts, v.total_downtime_hours,
               v.utilization_pct, v.avg_efficiency_pct, v.total_produced
        FROM machines m
        JOIN plants pl ON pl.plant_id = m.plant_id
        LEFT JOIN vw_machine_utilization v ON v.machine_id = m.machine_id
        WHERE m.machine_id = :mid
    """
    row = db.execute(text(sql), {"mid": machine_id}).mappings().fetchone()
    if not row:
        return None
    d = dict(row)
    overdue = db.execute(
        text("SELECT COUNT(*) FROM maintenance WHERE machine_id=:mid AND NOT is_completed AND start_datetime < NOW()"),
        {"mid": machine_id},
    ).scalar()
    d["overdue_maintenance"] = overdue
    return MachineDetailOut(**d)


def get_machine_downtime(
    db: Session,
    date_from: str | None = None,
    date_to: str | None = None,
    plant_id: int | None = None,
    top_n: int = 10,
):
    where, params = ["1=1"], {}
    if plant_id:  where.append("p.plant_id = :plant_id"); params["plant_id"] = plant_id
    if date_from: where.append("p.production_date >= :df"); params["df"] = date_from
    if date_to:   where.append("p.production_date <= :dt"); params["dt"] = date_to
    sql = f"""
        SELECT m.machine_name, pl.plant_name,
               ROUND(SUM(p.downtime_minutes)::NUMERIC/60, 2) AS downtime_hours,
               COUNT(*) AS shifts
        FROM production p
        JOIN machines m  ON m.machine_id = p.machine_id
        JOIN plants   pl ON pl.plant_id  = p.plant_id
        WHERE {' AND '.join(where)}
        GROUP BY m.machine_name, pl.plant_name
        ORDER BY downtime_hours DESC
        LIMIT :top_n
    """
    params["top_n"] = top_n
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]
