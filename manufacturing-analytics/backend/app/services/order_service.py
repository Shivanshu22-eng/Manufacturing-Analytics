"""Orders service."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import OrderOut


def get_orders(
    db: Session,
    page: int = 1, page_size: int = 50,
    product_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    customer: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    where, params = ["1=1"], {}
    if product_id: where.append("o.product_id = :pid");          params["pid"]     = product_id
    if status:     where.append("o.status = :status");           params["status"]  = status
    if priority:   where.append("o.priority = :priority");       params["priority"]= priority
    if customer:   where.append("o.customer_name ILIKE :cust");  params["cust"]    = f"%{customer}%"
    if date_from:  where.append("o.order_date >= :df");          params["df"]      = date_from
    if date_to:    where.append("o.order_date <= :dt");          params["dt"]      = date_to
    cond = " AND ".join(where)
    total  = db.execute(text(f"SELECT COUNT(*) FROM orders o WHERE {cond}"), params).scalar()
    offset = (page - 1) * page_size
    sql = f"""
        SELECT o.order_id, o.order_number, o.customer_name,
               o.product_id, pr.product_name,
               o.quantity_ordered, o.unit_price, o.total_amount,
               o.order_date, o.expected_delivery, o.actual_delivery,
               o.status, o.priority
        FROM orders o JOIN products pr ON pr.product_id = o.product_id
        WHERE {cond}
        ORDER BY o.order_date DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size; params["offset"] = offset
    rows = db.execute(text(sql), params).mappings().all()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [OrderOut(**dict(r)) for r in rows]}
