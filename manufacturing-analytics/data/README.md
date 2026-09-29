# Phase 1 — Synthetic Data Generation

## What This Phase Does

Generates **9 CSV files** containing realistic manufacturing data with consistent
foreign-key relationships. Every downstream phase (ETL, SQL, API, UI) consumes these CSVs.

## Files

```
data/
├── generate_data.py          # Main generator script
├── requirements.txt          # Python dependencies (pandas, numpy, faker)
├── raw/                      # Generated CSVs (git-ignored)
│   ├── plants.csv
│   ├── machines.csv
│   ├── products.csv
│   ├── production.csv
│   ├── quality_inspections.csv
│   ├── defects.csv
│   ├── maintenance.csv
│   ├── inventory.csv
│   └── orders.csv
└── schemas/
    └── data_dictionary.md    # Full column reference
```

## Dataset Summary

| Table                | Rows        |
|----------------------|-------------|
| plants               | 10          |
| machines             | 50          |
| products             | 100         |
| production           | 100,000     |
| quality_inspections  | 50,000      |
| defects              | ~20,000–30,000 (varies) |
| maintenance          | 30,000      |
| inventory            | 20,000      |
| orders               | 10,000      |

## How to Run

### Prerequisites
- Python 3.9+  *(Anaconda recommended)*
- pandas, numpy, faker

### Install Dependencies

```bash
# Using Anaconda Python
C:\Users\<you>\anaconda3\python.exe -m pip install -r requirements.txt

# Using any Python 3.9+
python -m pip install -r requirements.txt
```

### Generate Data

```bash
# From the data/ directory
python generate_data.py

# Custom seed or output directory
python generate_data.py --seed 123 --out-dir ./raw
```

### Expected Output

```
22:43:00  INFO     Manufacturing Analytics -- Data Generator
22:43:00  INFO     Simulation: 2023-01-01 -> 2024-12-31
22:43:00  INFO     Generating plants ...
22:43:00  INFO       -> 10 plants
22:43:00  INFO     Generating machines ...
22:43:00  INFO       -> 50 machines
...
22:43:45  INFO     Data generation complete.

Dataset Summary
--------------------------------------------
  plants                            10 rows
  machines                          50 rows
  products                         100 rows
  production                   100,000 rows
  quality_inspections           50,000 rows
  defects                       ~26,000 rows
  maintenance                   30,000 rows
  inventory                     20,000 rows
  orders                        10,000 rows
--------------------------------------------
  TOTAL                        ~236,160 rows
```

### Estimated Runtime

| Machine        | Approx. time |
|----------------|-------------|
| 8-core CPU     | ~60–90 sec  |
| 4-core CPU     | ~90–150 sec |

The defects step is the bottleneck (row-by-row loop). This is intentional
to keep the code readable — performance optimization is not a Phase 1 goal.

## FK Relationship Map

```
plants
  └── machines (plant_id)
        └── production (machine_id, plant_id)
              └── quality_inspections (production_id, machine_id, plant_id, product_id)
                    └── defects (inspection_id, production_id, ...)
        └── maintenance (machine_id, plant_id)

products
  └── production (product_id)
  └── quality_inspections (product_id)
  └── defects (product_id)
  └── inventory (product_id)
  └── orders (product_id)
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: faker` | Run `python -m pip install faker` |
| `ModuleNotFoundError: pandas` | Run `python -m pip install pandas numpy` |
| `Python was not found` | Use full path to Anaconda: `C:\Users\<you>\anaconda3\python.exe` |
| Script is slow at defects step | Normal — ~30K failed inspections × 1–3 defects each |
| CSV files not appearing | Check that `raw/` directory exists or pass `--out-dir ./raw` |

## What Phase 2 Uses

Phase 2 (PostgreSQL schema + ETL) reads these CSVs and:
- Creates normalized tables matching these column names exactly
- Adds proper PK/FK constraints, indexes, and CHECK constraints
- Loads the data via the ETL pipeline (Phase 3)
