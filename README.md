[README.md](https://github.com/user-attachments/files/32820233/README.md)
# Manufacturing-Analytics
End-to-end manufacturing analytics platform using Python, FastAPI, React, PostgreSQL &amp; Apache Superset, processing 100K+ records with 10+ operational KPIs and 5+ interactive dashboards.
<div align="center">

# 🏭 Manufacturing Intelligence & Operations Analytics Platform

**A production-grade, full-stack analytics platform for manufacturing operations**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Apache Superset](https://img.shields.io/badge/Apache-Superset-FF6B6B?style=for-the-badge&logo=apache&logoColor=white)](https://superset.apache.org)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Records](https://img.shields.io/badge/Dataset-250K%2B%20rows-brightgreen?style=flat-square)]()
[![Tables](https://img.shields.io/badge/Schema-9%20tables-blue?style=flat-square)]()
[![API Endpoints](https://img.shields.io/badge/REST%20API-19%20endpoints-orange?style=flat-square)]()

*Built as a portfolio project for a Data/BI Engineer internship application — B.Tech CSE, 4th Year*

</div>

---

## 📌 What This Project Demonstrates

This platform simulates a **real manufacturing company's data infrastructure** — from raw data ingestion to interactive dashboards and automated alerts. It is designed to showcase the full end-to-end data engineering lifecycle across 12 technologies:

| Skill Area | Technologies Used |
|---|---|
| **Data Modeling** | 9-table normalized PostgreSQL schema with FK constraints |
| **Advanced SQL** | Window functions, CTEs, JSON aggregation, lateral joins, views |
| **ETL Pipeline** | Python + Pandas + SQLAlchemy — validated batch loading |
| **REST API** | FastAPI with 19 endpoints, Pydantic schemas, ORM layer |
| **Data Visualization** | React + Recharts — 8 interactive dashboard pages |
| **BI Tooling** | Apache Superset connected to analytical SQL views |
| **DevOps** | Full Docker Compose stack (5 services, health checks) |
| **Business Analytics** | KPIs, OEE, defect tracking, inventory alerts, order fulfillment |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA GENERATION                          │
│         data/generate_data.py  →  data/raw/*.csv           │
│              250,000+ rows · 9 CSV files                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE                             │
│   etl/pipeline.py → validates → batch inserts into PG      │
│         pandas · SQLAlchemy · FK integrity checks           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   POSTGRESQL 16                             │
│  9 tables · 7 SQL Views · Performance Indexes               │
│  plants, machines, products, production, quality,           │
│  defects, maintenance, inventory, orders                    │
└──────────┬──────────────────────────────────┬──────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────┐               ┌──────────────────────┐
│   FASTAPI        │               │   APACHE SUPERSET    │
│   REST API       │               │   BI Dashboards      │
│   19 endpoints   │               │   SQL Views → Charts │
└────────┬─────────┘               └──────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   REACT FRONTEND                            │
│   8 pages · Recharts · React Router · Dark-mode UI         │
│   Dashboard · Production · Machines · Quality ·             │
│   Inventory · Maintenance · Orders · Alerts                 │
└─────────────────────────────────────────────────────────────┘

         All services orchestrated with Docker Compose
```

---

## ✨ Features

### 📊 Executive Dashboard
- **9 real-time KPI cards** — production runs, units produced, OEE efficiency, defect rate, downtime, revenue
- Monthly production trend (planned vs actual) — area chart
- Production breakdown by plant — horizontal bar chart
- Top machines by downtime — ranked bar chart
- Defect distribution by category — pie chart

### 🏭 Production Analytics
- Paginated production run history (50K+ records)
- Filter by date range, status, plant, machine, product
- Efficiency color-coding (green/yellow/red thresholds)

### ⚙️ Machine Management
- Full fleet status with live status indicators
- Machine utilization detail modal (OEE metrics, total downtime, avg efficiency)
- Top-10 machines by downtime ranking

### 🔬 Quality Control
- Defect trend line chart (monthly)
- Category breakdown pie chart
- Top defective machines ranking
- Filterable defect log (by severity, resolution status)

### 📦 Inventory Management
- Real-time stock status across all products
- Color-coded stock health (OK / Low Stock / Out of Stock)
- Monthly stock-in vs stock-out area chart
- Stock value calculation per product

### 🔧 Maintenance Tracking
- All / Overdue / Upcoming (30-day) tab switcher
- Filter by type (Preventive / Corrective / Predictive / Emergency)
- Cost tracking and technician assignment

### 📋 Order Management
- Customer name search (ILIKE)
- Filter by status, priority
- Late delivery highlighting (red)

### 🚨 Operational Alerts
- **5 auto-computed alert types** — no manual configuration needed
- Severity levels: Critical → High → Medium → Low
- High defect rate (>5%, rolling 30-day window)
- High machine downtime (>20% of shift)
- Low inventory / Out of stock
- Overdue maintenance tasks
- One-click refresh

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
plants ──────┬── machines ──┬── production ──── quality_inspections ── defects
             │              └── maintenance                ↑
             │                                       (FK to production)
             └── production (plant_id denormalized for BI query speed)

products ────┬── production
             ├── quality_inspections
             ├── defects
             ├── inventory
             └── orders
```

### Tables

| Table | Rows | Description |
|---|---|---|
| `plants` | 10 | Manufacturing plant locations across India |
| `machines` | ~120 | Equipment with type, manufacturer, capacity |
| `products` | ~50 | SKUs with cost, price, reorder levels |
| `production` | ~50,000 | Shift-level production records |
| `quality_inspections` | ~50,000 | Inspection results per production run |
| `defects` | ~30,000 | Defect records with category & severity |
| `maintenance` | ~10,000 | Maintenance tasks with cost & duration |
| `inventory` | ~50,000 | Stock transactions (IN / OUT / SCRAP / RETURN) |
| `orders` | ~20,000 | Customer orders with delivery tracking |
| **Total** | **~250,000+** | |

### SQL Analytical Views (for Superset + API)

| View | Purpose |
|---|---|
| `vw_dashboard_kpis` | Single-row executive metrics summary |
| `vw_plant_production_summary` | Monthly production aggregated by plant |
| `vw_machine_utilization` | OEE — utilization, efficiency, downtime per machine |
| `vw_defect_analysis` | Defect rate breakdown by plant, machine, category |
| `vw_inventory_status` | Latest stock level + reorder status per product |
| `vw_order_fulfillment` | On-time vs late delivery rate per product |
| `vw_maintenance_summary` | Maintenance cost, frequency, overdue count |

### Advanced SQL Techniques Used

```sql
-- Window functions
ROW_NUMBER() OVER (PARTITION BY plant_id ORDER BY production_date DESC)
LAG(total_qty, 1) OVER (ORDER BY month)   -- Month-over-month delta
RANK() OVER (ORDER BY defect_rate_pct DESC)

-- CTEs
WITH monthly_efficiency AS (
    SELECT DATE_TRUNC('month', production_date) AS month,
           AVG(efficiency_pct) AS avg_eff
    FROM production GROUP BY 1
)
SELECT *, avg_eff - LAG(avg_eff) OVER (ORDER BY month) AS mom_change
FROM monthly_efficiency;

-- Aggregation with FILTER
SUM(quantity) FILTER (WHERE transaction_type = 'IN')  AS total_in,
SUM(quantity) FILTER (WHERE transaction_type = 'OUT') AS total_out

-- JSON aggregation
json_agg(json_build_object('category', defect_category, 'count', cnt))

-- LATERAL join for top-N per group
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Min Version |
|---|---|
| Docker & Docker Compose | 24.0 |
| Python | 3.10 |
| Node.js | 18 |
| PostgreSQL (local dev only) | 15 |

---

### 🐳 Option A — Docker Compose (Recommended)

Spins up **all 5 services** (Postgres + ETL + Backend + Frontend + Superset) with one command.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/manufacturing-analytics.git
cd manufacturing-analytics

# 2. Configure environment
cp .env.example .env
# Open .env and set a secure POSTGRES_PASSWORD

# 3. Generate synthetic data (one-time, ~2 min)
cd data
pip install pandas numpy faker
python generate_data.py
cd ..

# 4. Launch all services
docker compose up -d

# 5. Load data into PostgreSQL (one-time ETL run)
docker compose run --rm etl

# 6. Open the application
#    React App   → http://localhost
#    API Docs    → http://localhost:8000/docs
#    Superset    → http://localhost:8088  (admin / admin123)
```

---

### 💻 Option B — Local Development

```bash
# ── 1. Environment ─────────────────────────────────────
cp .env.example .env    # set POSTGRES_PASSWORD

# ── 2. Database setup ──────────────────────────────────
psql -U postgres -c "CREATE USER mfg_user WITH PASSWORD 'yourpassword';"
psql -U postgres -c "CREATE DATABASE manufacturing_db OWNER mfg_user;"
psql -U mfg_user -d manufacturing_db -f sql/01_schema.sql
psql -U mfg_user -d manufacturing_db -f sql/02_indexes.sql
psql -U mfg_user -d manufacturing_db -f sql/views/01_kpi_views.sql

# ── 3. Synthetic data generation (~2 min) ──────────────
cd data
pip install pandas numpy faker
python generate_data.py
cd ..

# ── 4. ETL pipeline ────────────────────────────────────
cd etl
pip install -r requirements.txt
python pipeline.py        # loads all 9 CSVs into PostgreSQL
cd ..

# ── 5. FastAPI backend (Terminal 1) ────────────────────
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API Docs → http://localhost:8000/docs

# ── 6. React frontend (Terminal 2) ─────────────────────
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

---

## 📡 REST API Reference

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/kpis` | Executive KPI summary card |
| `GET` | `/api/dashboard/production-trend` | Production trend `?granularity=monthly\|weekly\|daily` |

### Production

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/production` | Paginated records `?page=1&page_size=50&status=Good` |
| `GET` | `/api/production/by-plant` | Aggregated output per plant |

### Machines

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/machines` | Fleet list `?plant_id=&status=Operational` |
| `GET` | `/api/machines/{id}` | Detail with utilization + OEE |
| `GET` | `/api/machines/downtime` | Top machines by downtime `?top_n=10` |

### Quality

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/quality/inspections` | Inspection records with filters |
| `GET` | `/api/quality/defects` | Defect log `?severity=High&is_resolved=false` |
| `GET` | `/api/quality/defect-summary` | Category breakdown with % |
| `GET` | `/api/quality/defect-trend` | Time-series defect count |
| `GET` | `/api/quality/top-defective-machines` | Worst machines by defect count |

### Maintenance

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/maintenance` | All records `?maintenance_type=Preventive` |
| `GET` | `/api/maintenance/overdue` | All incomplete + past-due tasks |
| `GET` | `/api/maintenance/upcoming` | Tasks due within 30 days |

### Inventory

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/inventory/status` | Latest stock level per product |
| `GET` | `/api/inventory` | Transaction history |
| `GET` | `/api/inventory/trend` | Monthly stock-in vs stock-out |

### Orders & Alerts

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/orders` | Orders `?status=Pending&priority=Urgent&customer=Tata` |
| `GET` | `/api/alerts` | Live business-rule alerts, sorted by severity |

---

## 🔔 Alert Engine

Alerts are **computed on-demand** directly from live database queries — no separate alerting table required.

```
┌─────────────────┬──────────────────────────────────┬───────────┐
│ Alert Type      │ Trigger Condition                │ Severity  │
├─────────────────┼──────────────────────────────────┼───────────┤
│ High Defect Rate│ > 5%  (30-day rolling window)    │ High      │
│ Critical Defects│ > 10% (30-day rolling window)    │ Critical  │
│ High Downtime   │ > 20% of total shift time        │ High      │
│ Low Inventory   │ current_stock < reorder_level    │ Medium    │
│ Out of Stock    │ current_stock = 0                │ Critical  │
│ Overdue Maint.  │ is_completed=false, past due date│ High      │
│ Critical Maint. │ 3+ overdue tasks on one machine  │ Critical  │
└─────────────────┴──────────────────────────────────┴───────────┘
```

---

## 📈 Apache Superset Setup

After starting with Docker Compose:

1. Open **http://localhost:8088** → Login: `admin / admin123`
2. Go to **Settings → Database Connections → + Database**
3. Choose **PostgreSQL**, URI:
   ```
   postgresql://mfg_user:<password>@postgres:5432/manufacturing_db
   ```
4. Build charts on top of the 7 analytical views
5. Create a dashboard and add **Native Filters** for Plant & Date

See [`superset/README.md`](superset/README.md) for recommended chart configurations.

---

## 📁 Project Structure

```
manufacturing-analytics/
│
├── 📂 data/
│   ├── generate_data.py          # Faker + NumPy → 9 normalized CSVs
│   ├── raw/                      # Generated CSVs (git-ignored)
│   └── schemas/data_dictionary.md
│
├── 📂 sql/
│   ├── 01_schema.sql             # DDL: 9 tables + FK + CHECK constraints
│   ├── 02_indexes.sql            # 15+ composite performance indexes
│   ├── views/01_kpi_views.sql    # 7 analytical views
│   └── analytics/01_advanced_queries.sql  # 10 demo queries (window fns, CTEs)
│
├── 📂 etl/
│   ├── pipeline.py               # Orchestrator: CSV → validate → PG
│   ├── validators.py             # Per-table validation + FK checks
│   ├── config.py                 # All config from env vars
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📂 backend/
│   └── app/
│       ├── main.py               # FastAPI entry + CORS
│       ├── database.py           # SQLAlchemy engine + session
│       ├── core/config.py        # Pydantic settings (env-based)
│       ├── models/               # 9 ORM models with relationships
│       ├── schemas/              # Pydantic response models
│       ├── services/             # Business logic (8 service modules)
│       └── routers/              # 8 API routers
│
├── 📂 frontend/
│   └── src/
│       ├── App.jsx               # Router + sidebar + topbar layout
│       ├── index.css             # Full dark-mode design system
│       ├── components/           # Sidebar, KPICard, Badge, Pagination...
│       ├── hooks/useApi.js       # Generic data-fetching hook
│       ├── services/api.js       # Axios API client (all 19 endpoints)
│       └── pages/                # Dashboard, Production, Machines,
│                                 # Quality, Inventory, Maintenance,
│                                 # Orders, Alerts
│
├── 📂 superset/
│   ├── superset_config.py        # Config: secret key, feature flags
│   ├── init.sh                   # Bootstrap: migrate + create admin
│   └── README.md                 # Dashboard setup guide
│
├── docker-compose.yml            # 5-service orchestration
├── .env.example                  # Template (never commit .env)
├── .gitignore
└── README.md
```

---

## 🧰 ETL Pipeline Design

```
CSV Files (data/raw/)
      │
      ▼
┌─────────────────────────────────────────┐
│          validators.py                  │
│  • Required column checks               │
│  • FK integrity (against live DB)       │
│  • Enum value normalization             │
│  • NULL filling with sensible defaults  │
│  • Business rule fixes (qty_passed +    │
│    qty_defective == qty_inspected)      │
│  • Duplicate row removal                │
└──────────────────┬──────────────────────┘
                   │ Clean DataFrame
                   ▼
┌─────────────────────────────────────────┐
│           pipeline.py                  │
│  • FK-ordered load sequence             │
│  • Batch inserts (default: 5,000 rows)  │
│  • NaN → NULL conversion                │
│  • Detailed logging to etl_run.log      │
│  • CLI: --tables, --truncate flags      │
└─────────────────────────────────────────┘
```

**Load order** (respects foreign key dependencies):  
`plants → machines → products → production → quality_inspections → defects → maintenance → inventory → orders`

---

## 🛠️ Local Dev Commands Reference

```bash
# Run ETL for a single table
python etl/pipeline.py --tables plants machines

# Truncate and reload specific tables
python etl/pipeline.py --tables production --truncate

# Run FastAPI with auto-reload
uvicorn app.main:app --reload --port 8000

# React dev server with HMR
cd frontend && npm run dev

# Docker: rebuild after code change
docker compose up -d --build backend

# Docker: view logs
docker compose logs -f backend
docker compose logs -f etl

# PostgreSQL: connect via psql
docker compose exec postgres psql -U mfg_user -d manufacturing_db
```

---

## 🌱 Environment Variables

Copy `.env.example` → `.env` and fill in your values:

```ini
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=manufacturing_db
POSTGRES_USER=mfg_user
POSTGRES_PASSWORD=your_secure_password_here

# ETL Behaviour
ETL_BATCH_SIZE=5000          # rows per insert batch
ETL_TRUNCATE=false           # set true to wipe tables before reload

# Apache Superset
SUPERSET_SECRET_KEY=long-random-string-here
SUPERSET_ADMIN_PASSWORD=admin123
```

> ⚠️ **Never commit `.env` to Git.** It is already in `.gitignore`.

---

## 🔍 Key Design Decisions

| Decision | Rationale |
|---|---|
| **Denormalized `plant_id` in production/defects** | Avoids multi-level joins in BI queries — significant perf gain |
| **SQL Views for Superset** | Decouples BI from raw tables; views can be evolved without breaking dashboards |
| **Alerts computed on-demand** | No stale alert state; always reflects current data |
| **ETL validators as a separate module** | Reusable, testable, and clear separation from loading logic |
| **FastAPI service layer** | Business logic isolated from HTTP routing — easier to test |
| **Pydantic settings** | All config from env vars, zero hardcoded secrets |
| **Vite proxy to FastAPI** | No CORS issues in dev; mirrors production nginx setup |

---

## 🧑‍💻 About

This project was built as a **portfolio piece** for a Data/BI Engineer internship at a product-based company. The goal was to demonstrate the complete data engineering lifecycle — not just coding ability, but also:

- Thinking about **data quality** (ETL validation layer)
- **Schema design** decisions (normalization vs denormalization trade-offs)
- **API design** (clean layered architecture)
- **BI tooling** integration (Superset on top of analytical views)
- **DevOps** awareness (Docker Compose with health checks and network isolation)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**If you found this useful, give it a ⭐ — it helps others discover the project!**

*Built with ❤️ by a B.Tech CSE student*

</div>
