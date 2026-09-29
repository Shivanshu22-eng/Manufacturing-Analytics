-- =============================================================================
-- Phase 2: KPI Views
-- File: sql/views/01_kpi_views.sql
-- All views used by FastAPI and Superset
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. vw_production_efficiency  — daily production summary per machine
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_production_efficiency AS
SELECT
    p.production_date,
    pl.plant_id,
    pl.plant_name,
    m.machine_id,
    m.machine_name,
    m.machine_type,
    pr.product_id,
    pr.product_name,
    pr.category AS product_category,
    COUNT(*)                                    AS shifts,
    SUM(p.planned_quantity)                     AS total_planned,
    SUM(p.actual_quantity)                      AS total_actual,
    ROUND(
        SUM(p.actual_quantity)::NUMERIC
        / NULLIF(SUM(p.planned_quantity), 0) * 100, 2
    )                                           AS efficiency_pct,
    SUM(p.downtime_minutes)                     AS total_downtime_min,
    ROUND(SUM(p.downtime_minutes)::NUMERIC
        / NULLIF(SUM(p.shift_duration_min), 0) * 100, 2)
                                                AS downtime_pct,
    COUNT(*) FILTER (WHERE p.status = 'Excellent') AS excellent_shifts,
    COUNT(*) FILTER (WHERE p.status = 'Poor')      AS poor_shifts
FROM production   p
JOIN plants       pl ON pl.plant_id   = p.plant_id
JOIN machines     m  ON m.machine_id  = p.machine_id
JOIN products     pr ON pr.product_id = p.product_id
GROUP BY
    p.production_date, pl.plant_id, pl.plant_name,
    m.machine_id, m.machine_name, m.machine_type,
    pr.product_id, pr.product_name, pr.category;

-- ---------------------------------------------------------------------------
-- 2. vw_defect_rate  — daily defect summary per product/machine
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_defect_rate AS
SELECT
    qi.inspection_date,
    pl.plant_id,
    pl.plant_name,
    m.machine_id,
    m.machine_name,
    pr.product_id,
    pr.product_name,
    pr.category AS product_category,
    COUNT(DISTINCT qi.inspection_id)                    AS inspections,
    SUM(qi.qty_inspected)                               AS total_inspected,
    SUM(qi.qty_defective)                               AS total_defective,
    ROUND(
        SUM(qi.qty_defective)::NUMERIC
        / NULLIF(SUM(qi.qty_inspected), 0) * 100, 4
    )                                                   AS overall_defect_rate_pct,
    COUNT(*) FILTER (WHERE qi.result = 'Failed')        AS failed_inspections,
    COUNT(*) FILTER (WHERE qi.result = 'Passed')        AS passed_inspections
FROM quality_inspections qi
JOIN plants    pl ON pl.plant_id   = qi.plant_id
JOIN machines  m  ON m.machine_id  = qi.machine_id
JOIN products  pr ON pr.product_id = qi.product_id
GROUP BY
    qi.inspection_date, pl.plant_id, pl.plant_name,
    m.machine_id, m.machine_name,
    pr.product_id, pr.product_name, pr.category;

-- ---------------------------------------------------------------------------
-- 3. vw_machine_utilization  — utilization & downtime per machine (all-time)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_machine_utilization AS
SELECT
    m.machine_id,
    m.machine_name,
    m.machine_type,
    m.status                                                AS current_status,
    pl.plant_id,
    pl.plant_name,
    m.last_maintenance_date,
    COUNT(p.production_id)                                  AS total_shifts,
    SUM(p.shift_duration_min)                               AS total_shift_min,
    SUM(p.downtime_minutes)                                 AS total_downtime_min,
    ROUND(
        (SUM(p.shift_duration_min) - SUM(p.downtime_minutes))::NUMERIC
        / NULLIF(SUM(p.shift_duration_min), 0) * 100, 2
    )                                                       AS utilization_pct,
    ROUND(SUM(p.downtime_minutes)::NUMERIC / 60, 2)        AS total_downtime_hours,
    SUM(p.planned_quantity)                                 AS total_planned,
    SUM(p.actual_quantity)                                  AS total_produced,
    ROUND(
        SUM(p.actual_quantity)::NUMERIC
        / NULLIF(SUM(p.planned_quantity), 0) * 100, 2
    )                                                       AS avg_efficiency_pct,
    MIN(p.production_date)                                  AS first_production_date,
    MAX(p.production_date)                                  AS last_production_date
FROM machines  m
JOIN plants    pl ON pl.plant_id  = m.plant_id
LEFT JOIN production p  ON p.machine_id = m.machine_id
GROUP BY
    m.machine_id, m.machine_name, m.machine_type,
    m.status, pl.plant_id, pl.plant_name, m.last_maintenance_date;

-- ---------------------------------------------------------------------------
-- 4. vw_inventory_status  — latest stock position per product
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_inventory_status AS
WITH latest AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        current_stock,
        reorder_level,
        is_below_reorder,
        transaction_date AS last_transaction_date,
        transaction_type AS last_transaction_type
    FROM inventory
    ORDER BY product_id, transaction_time DESC
)
SELECT
    p.product_id,
    p.product_name,
    p.product_code,
    p.category,
    p.unit_of_measure,
    p.unit_cost,
    l.current_stock,
    l.reorder_level,
    p.reorder_quantity,
    l.is_below_reorder,
    ROUND(l.current_stock * p.unit_cost, 2)    AS stock_value,
    l.last_transaction_date,
    l.last_transaction_type,
    CASE
        WHEN l.current_stock = 0          THEN 'Out of Stock'
        WHEN l.is_below_reorder           THEN 'Low Stock'
        WHEN l.current_stock < l.reorder_level * 1.5 THEN 'Watch'
        ELSE 'OK'
    END                                        AS stock_status
FROM products p
JOIN latest   l ON l.product_id = p.product_id
WHERE p.is_active = TRUE;

-- ---------------------------------------------------------------------------
-- 5. vw_maintenance_status  — per machine maintenance overview
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_maintenance_status AS
SELECT
    m.machine_id,
    m.machine_name,
    m.machine_type,
    pl.plant_id,
    pl.plant_name,
    m.status AS machine_status,
    COUNT(mt.maintenance_id)                        AS total_maintenance_events,
    COUNT(*) FILTER (WHERE mt.is_completed)         AS completed,
    COUNT(*) FILTER (WHERE NOT mt.is_completed)     AS pending,
    ROUND(SUM(mt.duration_hours) FILTER (WHERE mt.is_completed), 2) AS total_hours,
    ROUND(SUM(mt.cost), 2)                          AS total_cost,
    MAX(mt.end_datetime) FILTER (WHERE mt.is_completed)  AS last_completed_at,
    -- Next scheduled: earliest incomplete maintenance
    MIN(mt.start_datetime) FILTER (WHERE NOT mt.is_completed) AS next_scheduled_at,
    COUNT(*) FILTER (
        WHERE NOT mt.is_completed
        AND mt.start_datetime < NOW()
    )                                               AS overdue_count
FROM machines   m
JOIN plants     pl ON pl.plant_id    = m.plant_id
LEFT JOIN maintenance mt ON mt.machine_id = m.machine_id
GROUP BY
    m.machine_id, m.machine_name, m.machine_type,
    pl.plant_id, pl.plant_name, m.status;

-- ---------------------------------------------------------------------------
-- 6. vw_order_summary  — order fulfilment KPIs
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_order_summary AS
SELECT
    o.order_id,
    o.order_number,
    o.customer_name,
    p.product_id,
    p.product_name,
    p.category,
    o.quantity_ordered,
    o.unit_price,
    o.total_amount,
    o.order_date,
    o.expected_delivery,
    o.actual_delivery,
    o.status,
    o.priority,
    CASE
        WHEN o.actual_delivery IS NULL THEN NULL
        ELSE o.actual_delivery - o.expected_delivery
    END                                     AS delivery_variance_days,
    CASE
        WHEN o.status = 'Cancelled'                                 THEN 'Cancelled'
        WHEN o.actual_delivery IS NOT NULL
             AND o.actual_delivery <= o.expected_delivery           THEN 'On Time'
        WHEN o.actual_delivery IS NOT NULL
             AND o.actual_delivery > o.expected_delivery            THEN 'Late'
        WHEN o.actual_delivery IS NULL
             AND CURRENT_DATE > o.expected_delivery
             AND o.status NOT IN ('Completed','Shipped','Cancelled') THEN 'Overdue'
        ELSE 'In Progress'
    END                                     AS delivery_status
FROM orders  o
JOIN products p ON p.product_id = o.product_id;

-- ---------------------------------------------------------------------------
-- 7. vw_dashboard_kpis  — single-row executive summary
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_dashboard_kpis AS
SELECT
    -- Production
    (SELECT COUNT(*)            FROM production)                    AS total_production_runs,
    (SELECT SUM(actual_quantity) FROM production)                   AS total_units_produced,
    (SELECT ROUND(AVG(efficiency_pct),2) FROM production)          AS avg_efficiency_pct,

    -- Quality
    (SELECT ROUND(
        SUM(qty_defective)::NUMERIC / NULLIF(SUM(qty_inspected),0) * 100, 4
    ) FROM quality_inspections)                                     AS overall_defect_rate_pct,
    (SELECT COUNT(*) FROM defects WHERE NOT is_resolved)            AS open_defects,

    -- Machines
    (SELECT COUNT(*) FROM machines)                                 AS total_machines,
    (SELECT COUNT(*) FROM machines WHERE status = 'Operational')    AS operational_machines,
    (SELECT ROUND(
        AVG(
            (shift_duration_min - downtime_minutes)::NUMERIC
            / NULLIF(shift_duration_min, 0) * 100
        ), 2
    ) FROM production)                                             AS avg_utilization_pct,
    (SELECT ROUND(SUM(downtime_minutes)::NUMERIC / 60, 1)
     FROM production)                                              AS total_downtime_hours,

    -- Inventory
    (SELECT COUNT(*) FROM vw_inventory_status WHERE stock_status = 'Low Stock') AS low_stock_products,
    (SELECT COUNT(*) FROM vw_inventory_status WHERE stock_status = 'Out of Stock') AS out_of_stock,

    -- Maintenance
    (SELECT COUNT(*) FROM maintenance WHERE NOT is_completed
     AND start_datetime < NOW())                                    AS overdue_maintenance,

    -- Orders
    (SELECT COUNT(*) FROM orders WHERE status NOT IN ('Completed','Shipped','Cancelled')) AS active_orders,
    (SELECT ROUND(SUM(total_amount),2) FROM orders WHERE status IN ('Completed','Shipped')) AS revenue;

DO $$ BEGIN
    RAISE NOTICE 'Views created successfully: 7 views';
END $$;
