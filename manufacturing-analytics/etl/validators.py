"""
ETL Validators
Validates and cleans each DataFrame before database insertion.
"""
import logging
from datetime import datetime

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def _require_columns(df: pd.DataFrame, required: list[str], table: str):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValidationError(f"[{table}] Missing columns: {missing}")


def _report(df: pd.DataFrame, table: str, original_len: int):
    dropped = original_len - len(df)
    if dropped:
        log.warning("[%s] Dropped %d invalid rows (kept %d)", table, dropped, len(df))
    return df


# ---------------------------------------------------------------------------
# Plants
# ---------------------------------------------------------------------------
def validate_plants(df: pd.DataFrame) -> pd.DataFrame:
    _require_columns(df, ["plant_id","plant_name","city","state","capacity","established_year"], "plants")
    n = len(df)
    df = df.dropna(subset=["plant_id","plant_name","city","state"])
    df = df[df["capacity"].apply(lambda x: str(x).isdigit() and int(x) > 0)]
    df["is_active"] = df.get("is_active", True).fillna(True).astype(bool)
    df["created_at"] = pd.to_datetime(df.get("created_at", datetime.now()), utc=True, errors="coerce")
    df = df.drop_duplicates(subset=["plant_id"])
    return _report(df, "plants", n)


# ---------------------------------------------------------------------------
# Machines
# ---------------------------------------------------------------------------
def validate_machines(df: pd.DataFrame, valid_plant_ids: set) -> pd.DataFrame:
    _require_columns(df, ["machine_id","machine_name","plant_id","hourly_capacity"], "machines")
    n = len(df)
    df = df.dropna(subset=["machine_id","machine_name","plant_id"])
    df = df[df["plant_id"].isin(valid_plant_ids)]
    df = df[df["hourly_capacity"].apply(lambda x: pd.notna(x) and int(x) > 0)]
    valid_statuses = {"Operational","Under Maintenance","Idle","Decommissioned"}
    df["status"] = df["status"].where(df["status"].isin(valid_statuses), "Operational")
    df["installation_date"] = pd.to_datetime(df["installation_date"], errors="coerce").dt.date
    df["last_maintenance_date"] = pd.to_datetime(
        df.get("last_maintenance_date"), errors="coerce"
    ).dt.date
    df = df.drop_duplicates(subset=["machine_id"])
    return _report(df, "machines", n)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
def validate_products(df: pd.DataFrame) -> pd.DataFrame:
    _require_columns(df, ["product_id","product_name","product_code","unit_cost","selling_price"], "products")
    n = len(df)
    df = df.dropna(subset=["product_id","product_name","product_code"])
    df = df[df["unit_cost"].apply(lambda x: pd.notna(x) and float(x) >= 0)]
    df = df[df["selling_price"].apply(lambda x: pd.notna(x) and float(x) >= 0)]
    df["reorder_level"]    = df["reorder_level"].fillna(100).astype(int)
    df["reorder_quantity"] = df["reorder_quantity"].fillna(500).astype(int)
    df["weight_kg"]        = df["weight_kg"].fillna(1.0).astype(float)
    df["is_active"]        = df.get("is_active", True).fillna(True).astype(bool)
    df = df.drop_duplicates(subset=["product_code"])
    return _report(df, "products", n)


# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------
def validate_production(
    df: pd.DataFrame, valid_machine_ids: set, valid_plant_ids: set, valid_product_ids: set
) -> pd.DataFrame:
    _require_columns(
        df,
        ["production_id","machine_id","plant_id","product_id",
         "planned_quantity","actual_quantity","efficiency_pct"],
        "production",
    )
    n = len(df)
    df = df[df["machine_id"].isin(valid_machine_ids)]
    df = df[df["plant_id"].isin(valid_plant_ids)]
    df = df[df["product_id"].isin(valid_product_ids)]
    df = df[df["planned_quantity"].apply(lambda x: pd.notna(x) and int(x) > 0)]
    df = df[df["actual_quantity"].apply(lambda x: pd.notna(x) and int(x) >= 0)]
    df["downtime_minutes"]  = df["downtime_minutes"].fillna(0).astype(int).clip(lower=0)
    df["efficiency_pct"]    = df["efficiency_pct"].fillna(0).astype(float).clip(lower=0)
    df["production_date"]   = pd.to_datetime(df["production_date"], errors="coerce").dt.date
    df["shift_start"]       = pd.to_datetime(df["shift_start"], utc=True, errors="coerce")
    df["created_at"]        = pd.to_datetime(df.get("created_at"), utc=True, errors="coerce")
    df                      = df.dropna(subset=["production_date","shift_start"])
    valid_statuses = {"Excellent","Good","Average","Poor"}
    df["status"] = df["status"].where(df["status"].isin(valid_statuses), "Good")
    df = df.drop_duplicates(subset=["production_id"])
    return _report(df, "production", n)


# ---------------------------------------------------------------------------
# Quality Inspections
# ---------------------------------------------------------------------------
def validate_quality(
    df: pd.DataFrame, valid_production_ids: set, valid_machine_ids: set,
    valid_plant_ids: set, valid_product_ids: set
) -> pd.DataFrame:
    _require_columns(
        df,
        ["inspection_id","production_id","machine_id","plant_id","product_id",
         "qty_inspected","qty_passed","qty_defective","result"],
        "quality_inspections",
    )
    n = len(df)
    df = df[df["production_id"].isin(valid_production_ids)]
    df = df[df["machine_id"].isin(valid_machine_ids)]
    df = df[df["plant_id"].isin(valid_plant_ids)]
    df = df[df["product_id"].isin(valid_product_ids)]
    # Fix qty constraint: qty_passed + qty_defective must == qty_inspected
    df["qty_inspected"]  = df["qty_inspected"].astype(int)
    df["qty_defective"]  = df["qty_defective"].astype(int).clip(lower=0)
    df["qty_passed"]     = df["qty_inspected"] - df["qty_defective"]
    df["defect_rate_pct"]= df["defect_rate_pct"].fillna(0).astype(float).clip(lower=0)
    df = df[df["qty_inspected"] > 0]
    valid_results = {"Passed","Failed"}
    df["result"] = df["result"].where(df["result"].isin(valid_results), "Passed")
    df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce").dt.date
    df["inspection_time"] = pd.to_datetime(df["inspection_time"], utc=True, errors="coerce")
    df["created_at"]      = pd.to_datetime(df.get("created_at"), utc=True, errors="coerce")
    df["notes"]           = df.get("notes", "").fillna("")
    df = df.dropna(subset=["inspection_date","inspection_time"])
    df = df.drop_duplicates(subset=["inspection_id"])
    return _report(df, "quality_inspections", n)


# ---------------------------------------------------------------------------
# Defects
# ---------------------------------------------------------------------------
def validate_defects(
    df: pd.DataFrame, valid_inspection_ids: set, valid_production_ids: set
) -> pd.DataFrame:
    _require_columns(
        df,
        ["defect_id","inspection_id","production_id","defect_category","severity","qty_defective"],
        "defects",
    )
    n = len(df)
    df = df[df["inspection_id"].isin(valid_inspection_ids)]
    df = df[df["production_id"].isin(valid_production_ids)]
    df = df[df["qty_defective"].apply(lambda x: pd.notna(x) and int(x) > 0)]
    valid_severities = {"Low","Medium","High","Critical"}
    df["severity"] = df["severity"].where(df["severity"].isin(valid_severities), "Medium")
    df["is_resolved"]      = df.get("is_resolved", False).fillna(False).astype(bool)
    df["resolution_notes"] = df.get("resolution_notes", "").fillna("")
    df["defect_date"]      = pd.to_datetime(df["defect_date"], errors="coerce").dt.date
    df["created_at"]       = pd.to_datetime(df.get("created_at"), utc=True, errors="coerce")
    df = df.dropna(subset=["defect_date"])
    df = df.drop_duplicates(subset=["defect_id"])
    return _report(df, "defects", n)


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------
def validate_maintenance(df: pd.DataFrame, valid_machine_ids: set, valid_plant_ids: set) -> pd.DataFrame:
    _require_columns(
        df,
        ["maintenance_id","machine_id","plant_id","maintenance_type","start_datetime","cost"],
        "maintenance",
    )
    n = len(df)
    df = df[df["machine_id"].isin(valid_machine_ids)]
    df = df[df["plant_id"].isin(valid_plant_ids)]
    df["start_datetime"] = pd.to_datetime(df["start_datetime"], utc=True, errors="coerce")
    df["end_datetime"]   = pd.to_datetime(df.get("end_datetime"),   utc=True, errors="coerce")
    df["cost"]           = df["cost"].fillna(0).astype(float).clip(lower=0)
    df["is_completed"]   = df.get("is_completed", False).fillna(False).astype(bool)
    df["duration_hours"] = df.get("duration_hours", np.nan).astype(float)
    df["parts_replaced"] = df.get("parts_replaced", "None").fillna("None")
    df["description"]    = df.get("description", "").fillna("")
    df["technician_name"]= df.get("technician_name", "Unknown").fillna("Unknown")
    df = df.dropna(subset=["start_datetime"])
    df = df.drop_duplicates(subset=["maintenance_id"])
    return _report(df, "maintenance", n)


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------
def validate_inventory(df: pd.DataFrame, valid_product_ids: set) -> pd.DataFrame:
    _require_columns(
        df,
        ["transaction_id","product_id","transaction_type","quantity","current_stock"],
        "inventory",
    )
    n = len(df)
    df = df[df["product_id"].isin(valid_product_ids)]
    valid_types = {"IN","OUT","ADJUSTMENT","RETURN","SCRAP"}
    df = df[df["transaction_type"].isin(valid_types)]
    df = df[df["quantity"].apply(lambda x: pd.notna(x) and int(x) > 0)]
    df["current_stock"]    = df["current_stock"].fillna(0).astype(int).clip(lower=0)
    df["reorder_level"]    = df["reorder_level"].fillna(100).astype(int)
    df["is_below_reorder"] = df["is_below_reorder"].fillna(False).astype(bool)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.date
    df["transaction_time"] = pd.to_datetime(df.get("transaction_time"), utc=True, errors="coerce")
    df["unit_cost"]        = df["unit_cost"].fillna(0).astype(float)
    df["reference_doc"]    = df.get("reference_doc", "").fillna("")
    df["notes"]            = df.get("notes", "").fillna("")
    df["created_at"]       = pd.to_datetime(df.get("created_at"), utc=True, errors="coerce")
    df = df.dropna(subset=["transaction_date"])
    df = df.drop_duplicates(subset=["transaction_id"])
    return _report(df, "inventory", n)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
def validate_orders(df: pd.DataFrame, valid_product_ids: set) -> pd.DataFrame:
    _require_columns(
        df,
        ["order_id","order_number","customer_name","product_id",
         "quantity_ordered","unit_price","total_amount","order_date","status"],
        "orders",
    )
    n = len(df)
    df = df[df["product_id"].isin(valid_product_ids)]
    df = df.dropna(subset=["order_number","customer_name"])
    df = df[df["quantity_ordered"].apply(lambda x: pd.notna(x) and int(x) > 0)]
    valid_statuses = {"Pending","Confirmed","In Production","Completed","Shipped","Cancelled"}
    df["status"] = df["status"].where(df["status"].isin(valid_statuses), "Pending")
    valid_priorities = {"Low","Normal","High","Urgent"}
    df["priority"] = df.get("priority", "Normal").where(
        df.get("priority", "Normal").isin(valid_priorities), "Normal"
    )
    df["order_date"]        = pd.to_datetime(df["order_date"], errors="coerce").dt.date
    df["expected_delivery"] = pd.to_datetime(df["expected_delivery"], errors="coerce").dt.date
    df["actual_delivery"]   = pd.to_datetime(df.get("actual_delivery"), errors="coerce").dt.date
    df["notes"]             = df.get("notes", "").fillna("")
    df["created_at"]        = pd.to_datetime(df.get("created_at"), utc=True, errors="coerce")
    df = df.dropna(subset=["order_date","expected_delivery"])
    df = df.drop_duplicates(subset=["order_number"])
    return _report(df, "orders", n)
