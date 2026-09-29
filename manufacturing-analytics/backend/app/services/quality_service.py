"""Quality & Defects service."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import QualityOut, DefectOut, DefectSummary


def get_inspections(
    db: Session,
    page: int = 1, page_size: int = 50,
    plant_id: int | None = None,
    machine_id: int | None = None,
    product_id: int | None = None,
    result: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    where, params = ["1=1"], {}
    if plant_id:   where.append("qi.plant_id = :plant_id");     params["plant_id"]   = plant_id
    if machine_id: where.append("qi.machine_id = :machine_id"); params["machine_id"] = machine_id
    if product_id: where.append("qi.product_id = :product_id"); params["product_id"] = product_id
    if result:     where.append("qi.result = :result");         params["result"]     = result
    if date_from:  where.append("qi.inspection_date >= :df");   params["df"]         = date_from
    if date_to:    where.append("qi.inspection_date <= :dt");   params["dt"]         = date_to
    cond = " AND ".join(where)

    total = db.execute(text(f"SELECT COUNT(*) FROM quality_inspections qi WHERE {cond}"), params).scalar()
    offset = (page - 1) * page_size
    sql = f"""
        SELECT qi.inspection_id, qi.production_id, qi.machine_id,
               qi.plant_id, qi.product_id, pr.product_name,
               qi.inspection_date, qi.inspector_name,
               qi.qty_inspected, qi.qty_passed, qi.qty_defective,
               qi.defect_rate_pct, qi.result
        FROM quality_inspections qi
        JOIN products pr ON pr.product_id = qi.product_id
        WHERE {cond}
        ORDER BY qi.inspection_date DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size; params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [QualityOut(**dict(r)) for r in rows]}


def get_defect_summary(db: Session, date_from: str | None = None, date_to: str | None = None):
    where, params = ["1=1"], {}
    if date_from: where.append("defect_date >= :df"); params["df"] = date_from
    if date_to:   where.append("defect_date <= :dt"); params["dt"] = date_to
    sql = f"""
        SELECT defect_category,
               COUNT(*) AS count,
               SUM(qty_defective) AS qty_defective,
               ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER() * 100, 2) AS pct_of_total
        FROM defects WHERE {' AND '.join(where)}
        GROUP BY defect_category ORDER BY count DESC
    """
    rows = db.execute(text(sql), params).mappings().all()
    return [DefectSummary(**dict(r)) for r in rows]


def get_defects(
    db: Session,
    page: int = 1, page_size: int = 50,
    plant_id: int | None = None,
    product_id: int | None = None,
    severity: str | None = None,
    is_resolved: bool | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    where, params = ["1=1"], {}
    if plant_id:               where.append("d.plant_id = :plant_id");     params["plant_id"]   = plant_id
    if product_id:             where.append("d.product_id = :product_id"); params["product_id"] = product_id
    if severity:               where.append("d.severity = :severity");     params["severity"]   = severity
    if is_resolved is not None:where.append("d.is_resolved = :ir");        params["ir"]         = is_resolved
    if date_from:              where.append("d.defect_date >= :df");       params["df"]         = date_from
    if date_to:                where.append("d.defect_date <= :dt");       params["dt"]         = date_to
    cond = " AND ".join(where)
    total = db.execute(text(f"SELECT COUNT(*) FROM defects d WHERE {cond}"), params).scalar()
    offset = (page - 1) * page_size
    sql = f"""
        SELECT d.defect_id, d.inspection_id, d.machine_id, d.plant_id,
               d.product_id, pr.product_name,
               d.defect_category, d.defect_description,
               d.severity, d.qty_defective, d.defect_date, d.is_resolved
        FROM defects d JOIN products pr ON pr.product_id = d.product_id
        WHERE {cond}
        ORDER BY d.defect_date DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size; params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [DefectOut(**dict(r)) for r in rows]}


def get_defect_trend(db: Session, granularity: str = "monthly"):
    trunc = {"daily": "day", "weekly": "week", "monthly": "month"}.get(granularity, "month")
    sql = f"""
        SELECT TO_CHAR(DATE_TRUNC('{trunc}', defect_date), 'YYYY-MM-DD') AS period,
               COUNT(*) AS defect_count, SUM(qty_defective) AS qty_defective
        FROM defects
        GROUP BY DATE_TRUNC('{trunc}', defect_date)
        ORDER BY DATE_TRUNC('{trunc}', defect_date)
    """
    rows = db.execute(text(sql)).mappings().all()
    return [dict(r) for r in rows]


def get_top_defective_machines(db: Session, top_n: int = 10):
    sql = """
        SELECT m.machine_name, pl.plant_name,
               COUNT(d.defect_id) AS defect_count,
               SUM(d.qty_defective) AS qty_defective
        FROM defects d
        JOIN machines m  ON m.machine_id = d.machine_id
        JOIN plants   pl ON pl.plant_id  = d.plant_id
        GROUP BY m.machine_name, pl.plant_name
        ORDER BY defect_count DESC LIMIT :n
    """
    rows = db.execute(text(sql), {"n": top_n}).mappings().all()
    return [dict(r) for r in rows]
