"""
Dashboard & KPI service — queries the vw_dashboard_kpis view.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import DashboardKPIs, ProductionTrendPoint


def get_kpis(db: Session, plant_id: int | None = None) -> DashboardKPIs:
    row = db.execute(text("SELECT * FROM vw_dashboard_kpis")).mappings().fetchone()
    if not row:
        return DashboardKPIs(
            total_production_runs=0, total_units_produced=0, avg_efficiency_pct=0,
            overall_defect_rate_pct=0, open_defects=0, total_machines=0,
            operational_machines=0, avg_utilization_pct=0, total_downtime_hours=0,
            low_stock_products=0, out_of_stock=0, overdue_maintenance=0,
            active_orders=0, revenue=0,
        )
    return DashboardKPIs(
        total_production_runs   = int(row["total_production_runs"] or 0),
        total_units_produced    = int(row["total_units_produced"] or 0),
        avg_efficiency_pct      = float(row["avg_efficiency_pct"] or 0),
        overall_defect_rate_pct = float(row["overall_defect_rate_pct"] or 0),
        open_defects            = int(row["open_defects"] or 0),
        total_machines          = int(row["total_machines"] or 0),
        operational_machines    = int(row["operational_machines"] or 0),
        avg_utilization_pct     = float(row["avg_utilization_pct"] or 0),
        total_downtime_hours    = float(row["total_downtime_hours"] or 0),
        low_stock_products      = int(row["low_stock_products"] or 0),
        out_of_stock            = int(row["out_of_stock"] or 0),
        overdue_maintenance     = int(row["overdue_maintenance"] or 0),
        active_orders           = int(row["active_orders"] or 0),
        revenue                 = float(row["revenue"] or 0),
    )


def get_production_trend(
    db: Session,
    granularity: str = "monthly",
    plant_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[ProductionTrendPoint]:
    trunc = {"daily": "day", "weekly": "week", "monthly": "month"}.get(granularity, "month")
    where_clauses = ["1=1"]
    params: dict = {}
    if plant_id:
        where_clauses.append("plant_id = :plant_id")
        params["plant_id"] = plant_id
    if date_from:
        where_clauses.append("production_date >= :date_from")
        params["date_from"] = date_from
    if date_to:
        where_clauses.append("production_date <= :date_to")
        params["date_to"] = date_to

    sql = f"""
        SELECT
            TO_CHAR(DATE_TRUNC('{trunc}', production_date), 'YYYY-MM-DD') AS period,
            SUM(planned_quantity)   AS total_planned,
            SUM(actual_quantity)    AS total_actual,
            ROUND(AVG(efficiency_pct),2) AS efficiency_pct,
            ROUND(SUM(downtime_minutes)::NUMERIC / 60, 2) AS total_downtime_hours,
            COUNT(*) AS shifts
        FROM production
        WHERE {' AND '.join(where_clauses)}
        GROUP BY DATE_TRUNC('{trunc}', production_date)
        ORDER BY DATE_TRUNC('{trunc}', production_date)
    """
    rows = db.execute(text(sql), params).mappings().all()
    return [
        ProductionTrendPoint(
            period              = r["period"],
            total_planned       = int(r["total_planned"] or 0),
            total_actual        = int(r["total_actual"] or 0),
            efficiency_pct      = float(r["efficiency_pct"] or 0),
            total_downtime_hours= float(r["total_downtime_hours"] or 0),
            shifts              = int(r["shifts"] or 0),
        )
        for r in rows
    ]
