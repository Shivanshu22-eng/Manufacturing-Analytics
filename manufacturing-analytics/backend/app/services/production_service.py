"""Production service — queries and filters."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import ProductionOut, ProductionTrendPoint


def get_production_list(
    db: Session,
    page: int = 1, page_size: int = 50,
    plant_id: int | None = None,
    machine_id: int | None = None,
    product_id: int | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "production_date",
    sort_dir: str = "desc",
):
    ALLOWED_SORT = {
        "production_date", "efficiency_pct", "actual_quantity",
        "planned_quantity", "downtime_minutes", "status",
    }
    sort_col = sort_by if sort_by in ALLOWED_SORT else "production_date"
    direction = "DESC" if sort_dir.lower() == "desc" else "ASC"

    where, params = ["1=1"], {}
    if plant_id:   where.append("p.plant_id = :plant_id");     params["plant_id"]   = plant_id
    if machine_id: where.append("p.machine_id = :machine_id"); params["machine_id"] = machine_id
    if product_id: where.append("p.product_id = :product_id"); params["product_id"] = product_id
    if status:     where.append("p.status = :status");         params["status"]     = status
    if date_from:  where.append("p.production_date >= :df");   params["df"]         = date_from
    if date_to:    where.append("p.production_date <= :dt");   params["dt"]         = date_to

    cond = " AND ".join(where)
    count_sql = f"SELECT COUNT(*) FROM production p WHERE {cond}"
    total = db.execute(text(count_sql), params).scalar()

    offset = (page - 1) * page_size
    sql = f"""
        SELECT p.production_id, p.machine_id, m.machine_name,
               p.plant_id, pl.plant_name,
               p.product_id, pr.product_name,
               p.production_date, p.shift_duration_min,
               p.planned_quantity, p.actual_quantity,
               p.efficiency_pct, p.downtime_minutes, p.status
        FROM production p
        JOIN machines m  ON m.machine_id  = p.machine_id
        JOIN plants   pl ON pl.plant_id   = p.plant_id
        JOIN products pr ON pr.product_id = p.product_id
        WHERE {cond}
        ORDER BY p.{sort_col} {direction}
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size
    params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    data = [ProductionOut(**dict(r)) for r in rows]
    return {"total": total, "page": page, "page_size": page_size, "data": data}


def get_production_by_plant(db: Session, date_from: str | None = None, date_to: str | None = None):
    where, params = ["1=1"], {}
    if date_from: where.append("production_date >= :df"); params["df"] = date_from
    if date_to:   where.append("production_date <= :dt"); params["dt"] = date_to
    sql = f"""
        SELECT pl.plant_name,
               SUM(p.actual_quantity) AS total_actual,
               ROUND(AVG(p.efficiency_pct),2) AS avg_efficiency
        FROM production p
        JOIN plants pl ON pl.plant_id = p.plant_id
        WHERE {' AND '.join(where)}
        GROUP BY pl.plant_name ORDER BY total_actual DESC
    """
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]
