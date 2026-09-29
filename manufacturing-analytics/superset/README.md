# Superset Dashboard Setup Guide

## 1. Start Superset
```bash
docker compose up superset superset-db
```
Open: http://localhost:8088
Login: `admin / admin123`

## 2. Connect Manufacturing Database
1. **Settings → Database Connections → + Database**
2. Choose **PostgreSQL**
3. URI:
   ```
   postgresql://mfg_user:<password>@postgres:5432/manufacturing_db
   ```
4. Display Name: `Manufacturing Analytics`
5. Click **Test Connection** → **Connect**

## 3. Recommended Charts

### Chart 1 — OEE Gauge
- Dataset: `vw_dashboard_kpis`
- Chart type: **Big Number**
- Metric: `avg_efficiency_pct`

### Chart 2 — Production Trend
- Dataset: `vw_plant_production_summary`
- Chart type: **Time-series Area Chart**
- Time column: `production_month`
- Metric: `total_actual_quantity`
- Group By: `plant_name`

### Chart 3 — Defect Rate by Plant
- Dataset: `vw_defect_analysis`
- Chart type: **Bar Chart**
- X-axis: `plant_name`
- Metric: `defect_rate_pct` (AVG)

### Chart 4 — Machine Utilization Heatmap
- Dataset: `vw_machine_utilization`
- Chart type: **Pivot Table**
- Rows: `machine_name`
- Columns: `status`
- Metrics: `utilization_pct`

### Chart 5 — Low Stock Alerts Table
- Dataset: `vw_inventory_status`
- Chart type: **Table**
- Columns: `product_name`, `current_stock`, `reorder_level`, `stock_status`
- Filter: `stock_status IN ('Low Stock', 'Out of Stock')`

### Chart 6 — Monthly Revenue Trend
- Dataset: `orders`
- Chart type: **Line Chart**
- Time column: `order_date`
- Time grain: **Month**
- Metric: `SUM(total_amount)`

## 4. Create Dashboard
1. **Dashboards → + Dashboard**
2. Name: `Manufacturing Operations Overview`
3. Drag charts from step 3 onto the canvas
4. Add **Native Filters** for Plant and Date Range
5. Save & publish

## 5. SQL Views available for Superset
| View | Purpose |
|------|---------|
| `vw_dashboard_kpis` | Executive summary metrics |
| `vw_plant_production_summary` | Monthly production by plant |
| `vw_machine_utilization` | Machine efficiency metrics |
| `vw_defect_analysis` | Defect rate breakdown |
| `vw_inventory_status` | Current stock levels |
| `vw_order_fulfillment` | Order delivery performance |
| `vw_maintenance_summary` | Maintenance cost & schedule |
