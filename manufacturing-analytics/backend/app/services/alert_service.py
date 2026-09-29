"""
Alert service — generates business-rule alerts from live DB data.
No extra table needed; alerts are computed on-demand.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import AlertOut


ALERT_RULES = {
    "HIGH_DEFECT_RATE":     {"threshold": 5.0,  "severity": "high"},
    "CRITICAL_DEFECT_RATE": {"threshold": 10.0, "severity": "critical"},
    "HIGH_DOWNTIME":        {"threshold": 20.0, "severity": "high"},   # % of shift
    "LOW_INVENTORY":        {"threshold": 0,    "severity": "medium"},
    "OUT_OF_STOCK":         {"threshold": 0,    "severity": "critical"},
    "OVERDUE_MAINTENANCE":  {"threshold": 0,    "severity": "high"},
    "MACHINE_IDLE":         {"threshold": 0,    "severity": "low"},
}


def get_alerts(db: Session) -> list[AlertOut]:
    alerts: list[AlertOut] = []
    now = datetime.now(timezone.utc)
    aid = 1

    # ── 1. Defect Rate Alerts (per machine, last 30 days) ─────────────────
    sql = """
        SELECT qi.machine_id, m.machine_name, pl.plant_name,
               ROUND(
                   SUM(qi.qty_defective)::NUMERIC
                   / NULLIF(SUM(qi.qty_inspected),0) * 100, 2
               ) AS defect_rate_pct
        FROM quality_inspections qi
        JOIN machines m  ON m.machine_id = qi.machine_id
        JOIN plants   pl ON pl.plant_id  = qi.plant_id
        WHERE qi.inspection_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY qi.machine_id, m.machine_name, pl.plant_name
        HAVING SUM(qi.qty_defective)::NUMERIC
               / NULLIF(SUM(qi.qty_inspected),0) * 100 > 5
        ORDER BY defect_rate_pct DESC
        LIMIT 20
    """
    for r in db.execute(text(sql)).mappings():
        rate = float(r["defect_rate_pct"])
        sev  = "critical" if rate > 10 else "high"
        alerts.append(AlertOut(
            alert_id      = f"defect-{r['machine_id']}",
            alert_type    = "HIGH_DEFECT_RATE",
            severity      = sev,
            title         = f"High Defect Rate — {r['machine_name']}",
            message       = f"Defect rate {rate}% exceeds 5% threshold (last 30 days).",
            affected_entity = "machine",
            entity_id     = int(r["machine_id"]),
            entity_name   = r["machine_name"],
            plant_name    = r["plant_name"],
            timestamp     = now,
            is_active     = True,
            metric_value  = rate,
            threshold     = 5.0,
        ))
        aid += 1

    # ── 2. High Downtime Alerts (per machine, last 30 days) ───────────────
    sql = """
        SELECT p.machine_id, m.machine_name, pl.plant_name,
               ROUND(
                   SUM(p.downtime_minutes)::NUMERIC
                   / NULLIF(SUM(p.shift_duration_min),0) * 100, 2
               ) AS downtime_pct
        FROM production p
        JOIN machines m  ON m.machine_id = p.machine_id
        JOIN plants   pl ON pl.plant_id  = p.plant_id
        WHERE p.production_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY p.machine_id, m.machine_name, pl.plant_name
        HAVING SUM(p.downtime_minutes)::NUMERIC
               / NULLIF(SUM(p.shift_duration_min),0) * 100 > 20
        ORDER BY downtime_pct DESC
        LIMIT 20
    """
    for r in db.execute(text(sql)).mappings():
        pct = float(r["downtime_pct"])
        alerts.append(AlertOut(
            alert_id      = f"downtime-{r['machine_id']}",
            alert_type    = "HIGH_DOWNTIME",
            severity      = "high",
            title         = f"High Downtime — {r['machine_name']}",
            message       = f"Downtime is {pct}% of shift time, exceeding 20% threshold.",
            affected_entity = "machine",
            entity_id     = int(r["machine_id"]),
            entity_name   = r["machine_name"],
            plant_name    = r["plant_name"],
            timestamp     = now,
            is_active     = True,
            metric_value  = pct,
            threshold     = 20.0,
        ))

    # ── 3. Low Inventory / Out-of-Stock ───────────────────────────────────
    sql = """
        SELECT product_id, product_name, current_stock, reorder_level, stock_status
        FROM vw_inventory_status
        WHERE stock_status IN ('Low Stock', 'Out of Stock')
        ORDER BY current_stock ASC
        LIMIT 30
    """
    for r in db.execute(text(sql)).mappings():
        is_oos = r["stock_status"] == "Out of Stock"
        alerts.append(AlertOut(
            alert_id      = f"inventory-{r['product_id']}",
            alert_type    = "OUT_OF_STOCK" if is_oos else "LOW_INVENTORY",
            severity      = "critical" if is_oos else "medium",
            title         = f"{'Out of Stock' if is_oos else 'Low Stock'} — {r['product_name']}",
            message       = (
                f"Current stock: {r['current_stock']} units. "
                f"Reorder level: {r['reorder_level']} units."
            ),
            affected_entity = "product",
            entity_id     = int(r["product_id"]),
            entity_name   = r["product_name"],
            timestamp     = now,
            is_active     = True,
            metric_value  = float(r["current_stock"]),
            threshold     = float(r["reorder_level"]),
        ))

    # ── 4. Overdue Maintenance ────────────────────────────────────────────
    sql = """
        SELECT mt.machine_id, m.machine_name, pl.plant_name,
               COUNT(*) AS overdue_count,
               MIN(mt.start_datetime) AS earliest_overdue
        FROM maintenance mt
        JOIN machines m  ON m.machine_id = mt.machine_id
        JOIN plants   pl ON pl.plant_id  = mt.plant_id
        WHERE NOT mt.is_completed AND mt.start_datetime < NOW()
        GROUP BY mt.machine_id, m.machine_name, pl.plant_name
        ORDER BY overdue_count DESC
        LIMIT 20
    """
    for r in db.execute(text(sql)).mappings():
        cnt = int(r["overdue_count"])
        alerts.append(AlertOut(
            alert_id      = f"maint-{r['machine_id']}",
            alert_type    = "OVERDUE_MAINTENANCE",
            severity      = "critical" if cnt >= 3 else "high",
            title         = f"Overdue Maintenance — {r['machine_name']}",
            message       = f"{cnt} maintenance task(s) overdue. Earliest was due {r['earliest_overdue']}.",
            affected_entity = "machine",
            entity_id     = int(r["machine_id"]),
            entity_name   = r["machine_name"],
            plant_name    = r["plant_name"],
            timestamp     = now,
            is_active     = True,
            metric_value  = float(cnt),
            threshold     = 0,
        ))

    # Sort: critical → high → medium → low
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 4))
    return alerts
