"""
ETL Pipeline — Main entry point
Reads CSVs → validates → loads into PostgreSQL in dependency order.

Usage:
    python pipeline.py
    python pipeline.py --tables plants machines products
    python pipeline.py --truncate          # wipe tables before loading
"""
import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from config import config
from validators import (
    validate_plants, validate_machines, validate_products,
    validate_production, validate_quality, validate_defects,
    validate_maintenance, validate_inventory, validate_orders,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, config.log_level, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("etl_run.log"),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DB Engine
# ---------------------------------------------------------------------------

def get_engine():
    engine = create_engine(config.database_url, pool_pre_ping=True)
    # Verify connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    log.info("Database connection OK → %s:%s/%s", config.db_host, config.db_port, config.db_name)
    return engine


# ---------------------------------------------------------------------------
# Loader helpers
# ---------------------------------------------------------------------------

def load_csv(table: str) -> pd.DataFrame:
    path = Path(config.raw_data_dir) / f"{table}.csv"
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path, low_memory=False)
    log.info("  Loaded %-28s  %8d rows from %s", table, len(df), path.name)
    return df


def bulk_insert(df: pd.DataFrame, table: str, engine, batch_size: int = 5000) -> int:
    """Insert DataFrame in batches using pandas to_sql with COPY-like speed."""
    if df.empty:
        log.warning("  [%s] Empty DataFrame — skipping insert", table)
        return 0

    # Replace NaN/NaT with None so psycopg2 converts to SQL NULL
    df = df.replace({np.nan: None})
    # Ensure pandas NaT → None
    for col in df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
        df[col] = df[col].astype(object).where(df[col].notna(), None)

    total = 0
    for i in range(0, len(df), batch_size):
        chunk = df.iloc[i : i + batch_size]
        chunk.to_sql(table, engine, if_exists="append", index=False, method="multi")
        total += len(chunk)
        log.debug("  [%s] Inserted batch %d–%d", table, i, i + len(chunk))

    return total


def truncate_tables(engine, tables: list[str]):
    """Truncate in reverse dependency order."""
    order = [
        "defects", "quality_inspections", "production",
        "maintenance", "inventory", "orders",
        "machines", "products", "plants",
    ]
    to_truncate = [t for t in order if t in tables]
    with engine.begin() as conn:
        for t in to_truncate:
            conn.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE"))
            log.info("  Truncated: %s", t)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(selected_tables: list[str] | None = None, truncate: bool = False):
    t0 = time.time()
    log.info("=" * 60)
    log.info("Manufacturing Analytics ETL Pipeline")
    log.info("=" * 60)

    engine = get_engine()

    # Full load order (respects FK dependencies)
    ALL_TABLES = [
        "plants", "machines", "products", "production",
        "quality_inspections", "defects", "maintenance",
        "inventory", "orders",
    ]
    tables_to_run = selected_tables or ALL_TABLES

    if truncate:
        log.info("Truncating tables before load ...")
        truncate_tables(engine, tables_to_run)

    results: dict[str, int] = {}

    # ── PLANTS ────────────────────────────────────────────────────────────
    if "plants" in tables_to_run:
        log.info("Processing: plants")
        df = load_csv("plants")
        df = validate_plants(df)
        n  = bulk_insert(df, "plants", engine, config.batch_size)
        results["plants"] = n

    # ── MACHINES ─────────────────────────────────────────────────────────
    if "machines" in tables_to_run:
        log.info("Processing: machines")
        df = load_csv("machines")
        valid_plant_ids = set(pd.read_sql("SELECT plant_id FROM plants", engine)["plant_id"])
        df = validate_machines(df, valid_plant_ids)
        n  = bulk_insert(df, "machines", engine, config.batch_size)
        results["machines"] = n

    # ── PRODUCTS ─────────────────────────────────────────────────────────
    if "products" in tables_to_run:
        log.info("Processing: products")
        df = load_csv("products")
        df = validate_products(df)
        n  = bulk_insert(df, "products", engine, config.batch_size)
        results["products"] = n

    # ── PRODUCTION ───────────────────────────────────────────────────────
    if "production" in tables_to_run:
        log.info("Processing: production")
        df = load_csv("production")
        valid_machine_ids  = set(pd.read_sql("SELECT machine_id FROM machines", engine)["machine_id"])
        valid_plant_ids    = set(pd.read_sql("SELECT plant_id   FROM plants",   engine)["plant_id"])
        valid_product_ids  = set(pd.read_sql("SELECT product_id FROM products", engine)["product_id"])
        df = validate_production(df, valid_machine_ids, valid_plant_ids, valid_product_ids)
        n  = bulk_insert(df, "production", engine, config.batch_size)
        results["production"] = n

    # ── QUALITY INSPECTIONS ──────────────────────────────────────────────
    if "quality_inspections" in tables_to_run:
        log.info("Processing: quality_inspections")
        df = load_csv("quality_inspections")
        valid_production_ids = set(pd.read_sql("SELECT production_id FROM production", engine)["production_id"])
        valid_machine_ids    = set(pd.read_sql("SELECT machine_id FROM machines", engine)["machine_id"])
        valid_plant_ids      = set(pd.read_sql("SELECT plant_id   FROM plants",   engine)["plant_id"])
        valid_product_ids    = set(pd.read_sql("SELECT product_id FROM products", engine)["product_id"])
        df = validate_quality(df, valid_production_ids, valid_machine_ids, valid_plant_ids, valid_product_ids)
        n  = bulk_insert(df, "quality_inspections", engine, config.batch_size)
        results["quality_inspections"] = n

    # ── DEFECTS ──────────────────────────────────────────────────────────
    if "defects" in tables_to_run:
        log.info("Processing: defects")
        df = load_csv("defects")
        valid_inspection_ids = set(pd.read_sql("SELECT inspection_id FROM quality_inspections", engine)["inspection_id"])
        valid_production_ids = set(pd.read_sql("SELECT production_id FROM production", engine)["production_id"])
        df = validate_defects(df, valid_inspection_ids, valid_production_ids)
        n  = bulk_insert(df, "defects", engine, config.batch_size)
        results["defects"] = n

    # ── MAINTENANCE ──────────────────────────────────────────────────────
    if "maintenance" in tables_to_run:
        log.info("Processing: maintenance")
        df = load_csv("maintenance")
        valid_machine_ids = set(pd.read_sql("SELECT machine_id FROM machines", engine)["machine_id"])
        valid_plant_ids   = set(pd.read_sql("SELECT plant_id   FROM plants",   engine)["plant_id"])
        df = validate_maintenance(df, valid_machine_ids, valid_plant_ids)
        n  = bulk_insert(df, "maintenance", engine, config.batch_size)
        results["maintenance"] = n

    # ── INVENTORY ────────────────────────────────────────────────────────
    if "inventory" in tables_to_run:
        log.info("Processing: inventory")
        df = load_csv("inventory")
        valid_product_ids = set(pd.read_sql("SELECT product_id FROM products", engine)["product_id"])
        df = validate_inventory(df, valid_product_ids)
        n  = bulk_insert(df, "inventory", engine, config.batch_size)
        results["inventory"] = n

    # ── ORDERS ───────────────────────────────────────────────────────────
    if "orders" in tables_to_run:
        log.info("Processing: orders")
        df = load_csv("orders")
        valid_product_ids = set(pd.read_sql("SELECT product_id FROM products", engine)["product_id"])
        df = validate_orders(df, valid_product_ids)
        n  = bulk_insert(df, "orders", engine, config.batch_size)
        results["orders"] = n

    elapsed = round(time.time() - t0, 1)
    log.info("=" * 60)
    log.info("ETL Complete in %ss", elapsed)
    log.info("=" * 60)

    print("\nETL Summary")
    print("-" * 40)
    for table, count in results.items():
        print(f"  {table:<28} {count:>8,} rows loaded")
    print(f"\n  Total time: {elapsed}s")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manufacturing Analytics ETL")
    parser.add_argument(
        "--tables", nargs="+",
        choices=[
            "plants","machines","products","production",
            "quality_inspections","defects","maintenance",
            "inventory","orders",
        ],
        help="Run only specific tables (default: all)",
    )
    parser.add_argument(
        "--truncate", action="store_true",
        help="Truncate tables before loading (DANGEROUS in production)",
    )
    args = parser.parse_args()

    try:
        run_pipeline(selected_tables=args.tables, truncate=args.truncate)
    except Exception as e:
        log.exception("ETL failed: %s", e)
        sys.exit(1)
