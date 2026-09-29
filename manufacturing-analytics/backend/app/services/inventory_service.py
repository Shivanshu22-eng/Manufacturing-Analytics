"""Inventory service."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import InventoryOut, InventoryStatusOut


def get_inventory_status(db: Session):
    sql = "SELECT * FROM vw_inventory_status ORDER BY stock_status, product_name"
    rows = db.execute(text(sql)).mappings().all()
    return [InventoryStatusOut(**dict(r)) for r in rows]


def get_inventory_transactions(
    db: Session,
    page: int = 1, page_size: int = 50,
    product_id: int | None = None,
    transaction_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    where, params = ["1=1"], {}
    if product_id:        where.append("i.product_id = :pid");         params["pid"]  = product_id
    if transaction_type:  where.append("i.transaction_type = :ttype"); params["ttype"]= transaction_type
    if date_from:         where.append("i.transaction_date >= :df");   params["df"]   = date_from
    if date_to:           where.append("i.transaction_date <= :dt");   params["dt"]   = date_to
    cond = " AND ".join(where)
    total  = db.execute(text(f"SELECT COUNT(*) FROM inventory i WHERE {cond}"), params).scalar()
    offset = (page - 1) * page_size
    sql = f"""
        SELECT i.transaction_id, i.product_id, pr.product_name,
               pr.product_code, pr.category,
               i.transaction_type, i.quantity,
               i.transaction_date, i.unit_cost,
               i.current_stock, i.reorder_level, i.is_below_reorder
        FROM inventory i JOIN products pr ON pr.product_id = i.product_id
        WHERE {cond}
        ORDER BY i.transaction_date DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size; params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [InventoryOut(**dict(r)) for r in rows]}


def get_inventory_trend(db: Session, granularity: str = "monthly"):
    trunc = {"daily": "day", "weekly": "week", "monthly": "month"}.get(granularity, "month")
    sql = f"""
        SELECT TO_CHAR(DATE_TRUNC('{trunc}', transaction_date), 'YYYY-MM-DD') AS period,
               SUM(quantity) FILTER (WHERE transaction_type='IN')  AS total_in,
               SUM(quantity) FILTER (WHERE transaction_type='OUT') AS total_out,
               AVG(current_stock) AS avg_stock
        FROM inventory
        GROUP BY DATE_TRUNC('{trunc}', transaction_date)
        ORDER BY DATE_TRUNC('{trunc}', transaction_date)
    """
    rows = db.execute(text(sql)).mappings().all()
    return [dict(r) for r in rows]
