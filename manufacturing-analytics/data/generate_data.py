"""
Manufacturing Intelligence & Operations Analytics Platform
Phase 1: Synthetic Data Generator

Generates realistic manufacturing data with consistent FK relationships.

Output CSVs (written to data/raw/):
  plants.csv, machines.csv, products.csv, production.csv,
  quality_inspections.csv, defects.csv, maintenance.csv,
  inventory.csv, orders.csv

Usage:
  python generate_data.py
  python generate_data.py --seed 42 --out-dir ./raw
"""

import argparse
import logging
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Simulation window
SIM_START = datetime(2023, 1, 1)
SIM_END   = datetime(2024, 12, 31)
SIM_DAYS  = (SIM_END - SIM_START).days  # 730

# Record counts
N_PLANTS        = 10
N_MACHINES      = 50
N_PRODUCTS      = 100
N_PRODUCTION    = 100_000
N_QUALITY       = 50_000
N_MAINTENANCE   = 30_000
N_INVENTORY     = 20_000
N_ORDERS        = 10_000

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------
PLANT_LOCATIONS = [
    ("Mumbai",      "Maharashtra"),
    ("Pune",        "Maharashtra"),
    ("Chennai",     "Tamil Nadu"),
    ("Coimbatore",  "Tamil Nadu"),
    ("Ahmedabad",   "Gujarat"),
    ("Surat",       "Gujarat"),
    ("Hyderabad",   "Telangana"),
    ("Bengaluru",   "Karnataka"),
    ("Lucknow",     "Uttar Pradesh"),
    ("Jaipur",      "Rajasthan"),
]

MACHINE_TYPES = [
    "CNC Lathe", "CNC Milling Machine", "Hydraulic Press",
    "Injection Moulding Machine", "Welding Robot", "Conveyor System",
    "Assembly Robot", "Laser Cutter", "3D Printer", "Forklift",
]

PRODUCT_NAME_TEMPLATES = {
    "Engine Components":   ["Piston Ring", "Crankshaft", "Camshaft", "Connecting Rod",
                            "Valve Spring", "Oil Pump", "Timing Belt", "Cylinder Head"],
    "Transmission Parts":  ["Gear Shaft", "Clutch Disc", "Synchromesh Ring", "Drive Shaft",
                            "Differential Gear", "Torque Converter"],
    "Electrical Systems":  ["Alternator", "Starter Motor", "Wiring Harness",
                            "ECU Module", "Fuse Box", "Relay Switch"],
    "Body Panels":         ["Hood Panel", "Door Panel", "Fender Assembly", "Roof Panel",
                            "Trunk Lid", "Bumper Cover"],
    "Brake Systems":       ["Brake Disc", "Brake Pad", "Brake Caliper", "ABS Sensor",
                            "Master Cylinder"],
    "Suspension Parts":    ["Shock Absorber", "Coil Spring", "Control Arm", "Tie Rod",
                            "Ball Joint", "Stabilizer Bar"],
    "Exhaust Systems":     ["Catalytic Converter", "Muffler", "Exhaust Manifold",
                            "O2 Sensor", "Resonator"],
    "Fuel Systems":        ["Fuel Pump", "Fuel Injector", "Fuel Filter",
                            "Pressure Regulator", "Fuel Rail"],
    "Cooling Systems":     ["Radiator", "Water Pump", "Thermostat", "Cooling Fan",
                            "Intercooler", "Coolant Reservoir"],
    "Interior Components": ["Dashboard Panel", "Seat Frame", "Door Handle Assembly",
                            "HVAC Duct", "Instrument Cluster", "Centre Console"],
}

DEFECT_CATEGORIES = [
    "Dimensional Defect", "Surface Defect", "Material Defect",
    "Assembly Error", "Functional Failure", "Cosmetic Defect",
]

DEFECT_DESCRIPTIONS = {
    "Dimensional Defect":  ["Out-of-tolerance length", "Bore diameter oversize",
                            "Thread pitch error", "Flatness deviation"],
    "Surface Defect":      ["Surface scratch", "Burr on edge", "Corrosion spot",
                            "Porosity in casting"],
    "Material Defect":     ["Wrong alloy grade", "Hardness below spec",
                            "Micro-crack detected", "Inclusion in weld"],
    "Assembly Error":      ["Missing fastener", "Wrong torque applied",
                            "Component installed backwards", "Snap-fit not seated"],
    "Functional Failure":  ["Leak under pressure test", "Electrical open circuit",
                            "Motor does not start", "Sensor out of range"],
    "Cosmetic Defect":     ["Paint blister", "Uneven surface finish",
                            "Label misalignment", "Colour mismatch"],
}

MAINTENANCE_TYPES = [
    "Preventive Maintenance", "Corrective Maintenance", "Predictive Maintenance",
    "Condition-Based Maintenance", "Emergency Repair",
]

MAINTENANCE_DESCRIPTIONS = [
    "Lubrication and oil change", "Bearing replacement", "Belt and pulley inspection",
    "Calibration check", "Sensor cleaning and testing", "Hydraulic fluid top-up",
    "Electrical panel inspection", "Coolant flush", "Filter replacement",
    "Motor alignment check", "Emergency motor replacement", "Gearbox overhaul",
    "Vibration analysis and balancing", "Thermal imaging inspection",
    "Control board replacement",
]

TRANSACTION_TYPES  = ["IN", "OUT", "ADJUSTMENT", "RETURN", "SCRAP"]
ORDER_STATUSES     = ["Pending", "Confirmed", "In Production", "Completed", "Shipped", "Cancelled"]
MACHINE_STATUSES   = ["Operational", "Under Maintenance", "Idle", "Decommissioned"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_dates_sorted(start: datetime, end: datetime, n: int):
    total = int((end - start).total_seconds())
    offsets = sorted(random.randint(0, total) for _ in range(n))
    return [start + timedelta(seconds=s) for s in offsets]


def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_plants():
    log.info("Generating plants ...")
    rows = []
    for i, (city, state) in enumerate(PLANT_LOCATIONS, start=1):
        rows.append({
            "plant_id":         i,
            "plant_name":       f"{city} Manufacturing Plant",
            "city":             city,
            "state":            state,
            "country":          "India",
            "capacity":         random.randint(500, 2000),
            "established_year": random.randint(1995, 2015),
            "is_active":        True,
            "created_at":       SIM_START,
        })
    df = pd.DataFrame(rows)
    log.info("  -> %d plants", len(df))
    return df


def generate_machines(plants):
    log.info("Generating machines ...")
    plant_ids = plants["plant_id"].tolist()
    rows = []
    machine_id = 1

    for plant_id in plant_ids:
        n = random.randint(4, 6)
        est_year = int(plants.loc[plants.plant_id == plant_id, "established_year"].values[0])
        for _ in range(n):
            mtype = random.choice(MACHINE_TYPES)
            installed = datetime(est_year, 1, 1) + timedelta(
                days=random.randint(0, (datetime(2022, 12, 31) - datetime(est_year, 1, 1)).days)
            )
            rows.append({
                "machine_id":            machine_id,
                "machine_name":          f"{mtype} #{machine_id:03d}",
                "machine_type":          mtype,
                "plant_id":              plant_id,
                "model_number":          f"MDL-{random.randint(1000, 9999)}",
                "manufacturer":          fake.company(),
                "installation_date":     installed.date(),
                "last_maintenance_date": None,
                "status":                weighted_choice(MACHINE_STATUSES, [0.80, 0.10, 0.08, 0.02]),
                "hourly_capacity":       random.randint(20, 200),
                "created_at":            SIM_START,
            })
            machine_id += 1
            if machine_id > N_MACHINES:
                break
        if machine_id > N_MACHINES:
            break

    df = pd.DataFrame(rows)
    log.info("  -> %d machines", len(df))
    return df


def generate_products():
    log.info("Generating products ...")
    rows = []
    product_id = 1

    for category, templates in PRODUCT_NAME_TEMPLATES.items():
        for template in templates:
            for variant in ["Standard", "Premium", "Economy"]:
                unit_cost = round(random.uniform(50, 5000), 2)
                rows.append({
                    "product_id":       product_id,
                    "product_name":     f"{template} ({variant})",
                    "product_code":     f"PRD-{product_id:04d}",
                    "category":         category,
                    "unit_of_measure":  "Piece",
                    "unit_cost":        unit_cost,
                    "selling_price":    round(unit_cost * random.uniform(1.15, 1.50), 2),
                    "reorder_level":    random.randint(50, 500),
                    "reorder_quantity": random.randint(200, 2000),
                    "weight_kg":        round(random.uniform(0.1, 50.0), 3),
                    "is_active":        True,
                    "created_at":       SIM_START,
                })
                product_id += 1
                if product_id > N_PRODUCTS:
                    break
            if product_id > N_PRODUCTS:
                break
        if product_id > N_PRODUCTS:
            break

    df = pd.DataFrame(rows)
    log.info("  -> %d products", len(df))
    return df


def generate_production(machines, products):
    log.info("Generating production records ...")
    machine_ids   = machines["machine_id"].tolist()
    product_ids   = products["product_id"].tolist()
    machine_plant = machines.set_index("machine_id")["plant_id"].to_dict()
    machine_cap   = machines.set_index("machine_id")["hourly_capacity"].to_dict()

    dates       = rand_dates_sorted(SIM_START, SIM_END, N_PRODUCTION)
    m_ids       = np.random.choice(machine_ids, N_PRODUCTION)
    p_ids       = np.random.choice(product_ids, N_PRODUCTION)
    shift_hours = np.random.randint(4, 13, N_PRODUCTION)
    caps        = np.array([machine_cap[m] for m in m_ids])
    planned     = (caps * shift_hours).astype(int)

    eff_factor  = np.clip(np.random.normal(0.90, 0.10, N_PRODUCTION), 0.50, 1.15)
    actual      = np.maximum(1, (planned * eff_factor).astype(int))
    efficiency  = np.round(actual / planned * 100, 2)
    shift_min   = shift_hours * 60
    downtime_pct= np.random.beta(1, 9, N_PRODUCTION)
    downtime_min= np.round(shift_min * downtime_pct).astype(int)

    def status(e):
        if e >= 95: return "Excellent"
        if e >= 80: return "Good"
        if e >= 60: return "Average"
        return "Poor"

    df = pd.DataFrame({
        "production_id":       range(1, N_PRODUCTION + 1),
        "machine_id":          m_ids,
        "plant_id":            [machine_plant[m] for m in m_ids],
        "product_id":          p_ids,
        "production_date":     [d.date() for d in dates],
        "shift_start":         dates,
        "shift_duration_min":  shift_min,
        "planned_quantity":    planned,
        "actual_quantity":     actual,
        "efficiency_pct":      efficiency,
        "downtime_minutes":    downtime_min,
        "status":              [status(e) for e in efficiency],
        "created_at":          dates,
    })
    log.info("  -> %d production records", len(df))
    return df


def generate_quality_inspections(production):
    log.info("Generating quality inspection records ...")
    sampled = production.sample(n=N_QUALITY, replace=True, random_state=SEED).reset_index(drop=True)

    qty_frac     = np.random.uniform(0.05, 0.30, N_QUALITY)
    qty_inspected= np.maximum(1, (sampled["actual_quantity"].values * qty_frac).astype(int))
    defect_rate  = np.clip(np.random.beta(1.5, 25, N_QUALITY), 0, 0.20)
    qty_defective= np.maximum(0, (qty_inspected * defect_rate).astype(int))
    qty_passed   = qty_inspected - qty_defective
    defect_pct   = np.round(qty_defective / qty_inspected * 100, 4)
    results      = np.where(defect_pct > 5, "Failed", "Passed")

    inspector_pool = [fake.name() for _ in range(30)]
    inspectors     = np.random.choice(inspector_pool, N_QUALITY)
    offset_hours   = np.random.randint(1, 8, N_QUALITY)
    inspection_times = [
        pd.Timestamp(sampled.loc[i, "shift_start"]) + pd.Timedelta(hours=int(offset_hours[i]))
        for i in range(N_QUALITY)
    ]

    df = pd.DataFrame({
        "inspection_id":   range(1, N_QUALITY + 1),
        "production_id":   sampled["production_id"].values,
        "machine_id":      sampled["machine_id"].values,
        "plant_id":        sampled["plant_id"].values,
        "product_id":      sampled["product_id"].values,
        "inspection_date": [t.date() for t in inspection_times],
        "inspection_time": inspection_times,
        "inspector_name":  inspectors,
        "qty_inspected":   qty_inspected,
        "qty_passed":      qty_passed,
        "qty_defective":   qty_defective,
        "defect_rate_pct": defect_pct,
        "result":          results,
        "notes":           "",
        "created_at":      inspection_times,
    })
    log.info("  -> %d quality inspections", len(df))
    return df


def generate_defects(quality_inspections):
    log.info("Generating defect records ...")
    failed = quality_inspections[quality_inspections["result"] == "Failed"].copy()

    rows = []
    defect_id = 1
    for _, insp in failed.iterrows():
        n_defects = random.randint(1, 3)
        for _ in range(n_defects):
            cat  = random.choice(DEFECT_CATEGORIES)
            desc = random.choice(DEFECT_DESCRIPTIONS[cat])
            sev  = weighted_choice(["Low", "Medium", "High", "Critical"], [0.30, 0.40, 0.20, 0.10])
            rows.append({
                "defect_id":          defect_id,
                "inspection_id":      insp["inspection_id"],
                "production_id":      insp["production_id"],
                "machine_id":         insp["machine_id"],
                "plant_id":           insp["plant_id"],
                "product_id":         insp["product_id"],
                "defect_category":    cat,
                "defect_description": desc,
                "severity":           sev,
                "qty_defective":      max(1, int(insp["qty_defective"] / n_defects)),
                "defect_date":        insp["inspection_date"],
                "is_resolved":        random.random() < 0.75,
                "resolution_notes":   "Fixed" if random.random() < 0.75 else "",
                "created_at":         insp["created_at"],
            })
            defect_id += 1

    df = pd.DataFrame(rows)
    log.info("  -> %d defect records", len(df))
    return df


def generate_maintenance(machines):
    log.info("Generating maintenance records ...")
    machine_ids   = machines["machine_id"].tolist()
    machine_plant = machines.set_index("machine_id")["plant_id"].to_dict()
    technician_pool = [fake.name() for _ in range(20)]

    rows = []
    maint_id   = 1
    per_machine = N_MAINTENANCE // N_MACHINES
    remainder   = N_MAINTENANCE % N_MACHINES

    for idx, mid in enumerate(machine_ids):
        n = per_machine + (1 if idx < remainder else 0)
        dates = rand_dates_sorted(SIM_START, SIM_END, n)
        for d in dates:
            mtype    = weighted_choice(MAINTENANCE_TYPES, [0.40, 0.25, 0.15, 0.10, 0.10])
            desc     = random.choice(MAINTENANCE_DESCRIPTIONS)
            duration = round(random.uniform(0.5, 16.0), 2)
            cost     = round(random.uniform(500, 50_000), 2)
            end_dt   = d + timedelta(hours=duration)
            completed= end_dt <= SIM_END and random.random() < 0.95

            rows.append({
                "maintenance_id":   maint_id,
                "machine_id":       mid,
                "plant_id":         machine_plant[mid],
                "maintenance_type": mtype,
                "description":      desc,
                "technician_name":  random.choice(technician_pool),
                "start_datetime":   d,
                "end_datetime":     end_dt if completed else None,
                "duration_hours":   duration if completed else None,
                "cost":             cost,
                "is_completed":     completed,
                "parts_replaced":   random.choice([
                    "Bearing", "Belt", "Filter", "Oil", "Sensor",
                    "Motor", "Pump", "Valve", "None", "None", "None",
                ]),
                "created_at":       d,
            })
            maint_id += 1

    df = pd.DataFrame(rows)
    log.info("  -> %d maintenance records", len(df))
    return df


def update_machine_last_maintenance(machines, maintenance):
    last_maint = (
        maintenance[maintenance["is_completed"]]
        .groupby("machine_id")["end_datetime"]
        .max()
        .reset_index()
        .rename(columns={"end_datetime": "last_maintenance_date"})
    )
    machines = machines.copy()
    machines["last_maintenance_date"] = machines["machine_id"].map(
        last_maint.set_index("machine_id")["last_maintenance_date"]
    )
    machines["last_maintenance_date"] = machines["last_maintenance_date"].apply(
        lambda x: x.date() if pd.notna(x) and hasattr(x, "date") else None
    )
    return machines


def generate_inventory(products):
    log.info("Generating inventory transactions ...")
    product_ids    = products["product_id"].tolist()
    product_reorder= products.set_index("product_id")["reorder_level"].to_dict()
    product_cost   = products.set_index("product_id")["unit_cost"].to_dict()

    dates   = rand_dates_sorted(SIM_START, SIM_END, N_INVENTORY)
    p_ids   = np.random.choice(product_ids, N_INVENTORY)
    tx_types= random.choices(TRANSACTION_TYPES, weights=[0.35, 0.45, 0.08, 0.07, 0.05], k=N_INVENTORY)

    running_qty = {pid: random.randint(100, 5000) for pid in product_ids}

    rows = []
    for i in range(N_INVENTORY):
        pid   = int(p_ids[i])
        ttype = tx_types[i]
        d     = dates[i]

        if ttype == "IN":
            qty = random.randint(100, 2000)
        elif ttype == "OUT":
            qty = random.randint(1, min(500, max(1, running_qty[pid])))
        elif ttype == "ADJUSTMENT":
            qty = random.randint(1, 50)
        elif ttype == "RETURN":
            qty = random.randint(1, 50)
        else:  # SCRAP
            qty = random.randint(1, 20)

        if ttype in ("IN", "RETURN"):
            running_qty[pid] += qty
        else:
            running_qty[pid] = max(0, running_qty[pid] - qty)

        reorder = product_reorder[pid]
        rows.append({
            "transaction_id":   i + 1,
            "product_id":       pid,
            "transaction_type": ttype,
            "quantity":         qty,
            "transaction_date": d.date(),
            "transaction_time": d,
            "unit_cost":        product_cost[pid],
            "reference_doc":    f"REF-{random.randint(10000, 99999)}",
            "notes":            "",
            "current_stock":    running_qty[pid],
            "reorder_level":    reorder,
            "is_below_reorder": running_qty[pid] < reorder,
            "created_at":       d,
        })

    df = pd.DataFrame(rows)
    log.info("  -> %d inventory transactions", len(df))
    return df


def generate_orders(products):
    log.info("Generating orders ...")
    product_ids   = products["product_id"].tolist()
    product_prices= products.set_index("product_id")["selling_price"].to_dict()
    customer_pool = [fake.company() for _ in range(50)]
    dates         = rand_dates_sorted(SIM_START, SIM_END, N_ORDERS)

    rows = []
    for i, d in enumerate(dates):
        pid           = random.choice(product_ids)
        qty           = random.randint(10, 5000)
        price         = product_prices[pid]
        total         = round(qty * price, 2)
        delivery_days = random.randint(7, 60)
        delivery_date = d + timedelta(days=delivery_days)
        status        = weighted_choice(ORDER_STATUSES, [0.05, 0.10, 0.15, 0.40, 0.25, 0.05])
        actual_delivery = None
        if status in ("Completed", "Shipped"):
            delay = random.randint(-3, 10)
            actual_delivery = (delivery_date + timedelta(days=delay)).date()

        rows.append({
            "order_id":          i + 1,
            "order_number":      f"ORD-{d.year}-{i + 1:05d}",
            "customer_name":     random.choice(customer_pool),
            "product_id":        pid,
            "quantity_ordered":  qty,
            "unit_price":        price,
            "total_amount":      total,
            "order_date":        d.date(),
            "expected_delivery": delivery_date.date(),
            "actual_delivery":   actual_delivery,
            "status":            status,
            "priority":          weighted_choice(["Low", "Normal", "High", "Urgent"],
                                                 [0.10, 0.55, 0.25, 0.10]),
            "notes":             "",
            "created_at":        d,
        })

    df = pd.DataFrame(rows)
    log.info("  -> %d orders", len(df))
    return df


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_fk(child_df, child_col, parent_df, parent_col, label):
    orphans = ~child_df[child_col].isin(parent_df[parent_col])
    if orphans.any():
        log.error("FK VIOLATION in %s: %d orphan rows in column '%s'", label, orphans.sum(), child_col)
    else:
        log.info("  FK OK: %s.%s", label, child_col)


def run_validation(tables):
    log.info("Running FK validation ...")
    validate_fk(tables["machines"],            "plant_id",      tables["plants"],              "plant_id",      "machines")
    validate_fk(tables["production"],          "machine_id",    tables["machines"],            "machine_id",    "production")
    validate_fk(tables["production"],          "plant_id",      tables["plants"],              "plant_id",      "production")
    validate_fk(tables["production"],          "product_id",    tables["products"],            "product_id",    "production")
    validate_fk(tables["quality_inspections"], "production_id", tables["production"],          "production_id", "quality")
    validate_fk(tables["quality_inspections"], "machine_id",    tables["machines"],            "machine_id",    "quality")
    validate_fk(tables["quality_inspections"], "product_id",    tables["products"],            "product_id",    "quality")
    validate_fk(tables["defects"],             "inspection_id", tables["quality_inspections"], "inspection_id", "defects")
    validate_fk(tables["maintenance"],         "machine_id",    tables["machines"],            "machine_id",    "maintenance")
    validate_fk(tables["inventory"],           "product_id",    tables["products"],            "product_id",    "inventory")
    validate_fk(tables["orders"],              "product_id",    tables["products"],            "product_id",    "orders")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir="raw"):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    log.info("=" * 60)
    log.info("Manufacturing Analytics -- Data Generator")
    log.info("Simulation: %s -> %s", SIM_START.date(), SIM_END.date())
    log.info("=" * 60)

    plants      = generate_plants()
    machines    = generate_machines(plants)
    products    = generate_products()
    production  = generate_production(machines, products)
    quality     = generate_quality_inspections(production)
    defects     = generate_defects(quality)
    maintenance = generate_maintenance(machines)
    machines    = update_machine_last_maintenance(machines, maintenance)
    inventory   = generate_inventory(products)
    orders      = generate_orders(products)

    tables = {
        "plants":               plants,
        "machines":             machines,
        "products":             products,
        "production":           production,
        "quality_inspections":  quality,
        "defects":              defects,
        "maintenance":          maintenance,
        "inventory":            inventory,
        "orders":               orders,
    }

    run_validation(tables)

    log.info("Writing CSVs to %s ...", out_path.resolve())
    for name, df in tables.items():
        fpath = out_path / f"{name}.csv"
        df.to_csv(fpath, index=False)
        log.info("  saved %-28s  %8d rows", fpath.name, len(df))

    log.info("=" * 60)
    log.info("Data generation complete.")
    log.info("=" * 60)

    print("\nDataset Summary")
    print("-" * 44)
    for name, df in tables.items():
        print(f"  {name:<28} {len(df):>10,} rows")
    print("-" * 44)
    total = sum(len(df) for df in tables.values())
    print(f"  {'TOTAL':<28} {total:>10,} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic manufacturing data")
    parser.add_argument("--seed",    type=int, default=42,    help="Random seed (default: 42)")
    parser.add_argument("--out-dir", type=str, default="raw", help="Output directory (default: raw)")
    args = parser.parse_args()

    SEED = args.seed
    random.seed(SEED)
    np.random.seed(SEED)
    Faker.seed(SEED)

    main(out_dir=args.out_dir)
