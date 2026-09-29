-- =============================================================================
-- Phase 2: Advanced Analytical SQL
-- File: sql/analytics/01_advanced_queries.sql
-- Demonstrates: CTEs, window functions, RANK, ROW_NUMBER, LAG, LEAD,
--               conditional aggregation, subqueries, date aggregation
-- =============================================================================


-- ============================================================
-- QUERY 1: Monthly Production Trend with MoM Growth (LAG)
-- ============================================================
WITH monthly_production AS (
    SELECT
        DATE_TRUNC('month', production_date)    AS month,
        SUM(actual_quantity)                    AS total_produced,
        ROUND(AVG(efficiency_pct), 2)           AS avg_efficiency,
        SUM(downtime_minutes)                   AS total_downtime_min
    FROM production
    GROUP BY DATE_TRUNC('month', production_date)
),
with_growth AS (
    SELECT
        month,
        total_produced,
        avg_efficiency,
        total_downtime_min,
        LAG(total_produced) OVER (ORDER BY month) AS prev_month_produced,
        ROUND(
            (total_produced - LAG(total_produced) OVER (ORDER BY month))::NUMERIC
            / NULLIF(LAG(total_produced) OVER (ORDER BY month), 0) * 100, 2
        ) AS mom_growth_pct
    FROM monthly_production
)
SELECT * FROM with_growth ORDER BY month;


-- ============================================================
-- QUERY 2: Machine Downtime Ranking per Plant (RANK, DENSE_RANK)
-- ============================================================
WITH machine_downtime AS (
    SELECT
        p.plant_id,
        pl.plant_name,
        p.machine_id,
        m.machine_name,
        m.machine_type,
        SUM(p.downtime_minutes)     AS total_downtime_min,
        ROUND(SUM(p.downtime_minutes)::NUMERIC / 60, 2) AS downtime_hours,
        COUNT(*)                    AS shifts
    FROM production p
    JOIN machines m  ON m.machine_id  = p.machine_id
    JOIN plants   pl ON pl.plant_id   = p.plant_id
    GROUP BY p.plant_id, pl.plant_name, p.machine_id, m.machine_name, m.machine_type
)
SELECT
    plant_name,
    machine_name,
    machine_type,
    downtime_hours,
    shifts,
    RANK()        OVER (PARTITION BY plant_id ORDER BY total_downtime_min DESC) AS plant_rank,
    DENSE_RANK()  OVER (ORDER BY total_downtime_min DESC)                       AS global_rank
FROM machine_downtime
ORDER BY global_rank;


-- ============================================================
-- QUERY 3: Top 10 Defective Products with Running Total (SUM OVER)
-- ============================================================
WITH product_defects AS (
    SELECT
        pr.product_id,
        pr.product_name,
        pr.category,
        SUM(d.qty_defective)    AS total_defective,
        COUNT(d.defect_id)      AS defect_events,
        COUNT(DISTINCT d.defect_category) AS defect_category_count
    FROM defects  d
    JOIN products pr ON pr.product_id = d.product_id
    GROUP BY pr.product_id, pr.product_name, pr.category
)
SELECT
    product_name,
    category,
    total_defective,
    defect_events,
    defect_category_count,
    ROUND(
        total_defective::NUMERIC / SUM(total_defective) OVER () * 100, 2
    )                               AS pct_of_all_defects,
    SUM(total_defective) OVER (
        ORDER BY total_defective DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                               AS running_total_defective
FROM product_defects
ORDER BY total_defective DESC
LIMIT 10;


-- ============================================================
-- QUERY 4: Weekly Defect Rate Trend with 4-Week Moving Average
-- ============================================================
WITH weekly AS (
    SELECT
        DATE_TRUNC('week', inspection_date) AS week_start,
        SUM(qty_inspected)      AS total_inspected,
        SUM(qty_defective)      AS total_defective,
        ROUND(
            SUM(qty_defective)::NUMERIC / NULLIF(SUM(qty_inspected),0) * 100, 4
        )                       AS defect_rate_pct
    FROM quality_inspections
    GROUP BY DATE_TRUNC('week', inspection_date)
)
SELECT
    week_start,
    total_inspected,
    total_defective,
    defect_rate_pct,
    ROUND(AVG(defect_rate_pct) OVER (
        ORDER BY week_start
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 4) AS moving_avg_4w,
    LAG(defect_rate_pct, 1) OVER (ORDER BY week_start) AS prev_week_rate,
    LEAD(defect_rate_pct, 1) OVER (ORDER BY week_start) AS next_week_rate
FROM weekly
ORDER BY week_start;


-- ============================================================
-- QUERY 5: Production Efficiency Percentile Buckets (NTILE)
-- ============================================================
SELECT
    machine_id,
    production_date,
    efficiency_pct,
    NTILE(4) OVER (ORDER BY efficiency_pct) AS efficiency_quartile,
    CASE NTILE(4) OVER (ORDER BY efficiency_pct)
        WHEN 1 THEN 'Bottom 25%'
        WHEN 2 THEN 'Lower Middle'
        WHEN 3 THEN 'Upper Middle'
        WHEN 4 THEN 'Top 25%'
    END AS quartile_label
FROM production
ORDER BY efficiency_pct DESC
LIMIT 100;


-- ============================================================
-- QUERY 6: Machines Needing Immediate Attention (CTE + subquery)
-- ============================================================
WITH machine_kpis AS (
    SELECT
        m.machine_id,
        m.machine_name,
        m.machine_type,
        pl.plant_name,
        m.status,
        m.last_maintenance_date,
        -- Days since last maintenance
        CURRENT_DATE - m.last_maintenance_date AS days_since_maintenance,
        -- Recent downtime (last 30 days)
        (SELECT ROUND(SUM(p2.downtime_minutes)::NUMERIC / 60, 2)
         FROM production p2
         WHERE p2.machine_id = m.machine_id
           AND p2.production_date >= CURRENT_DATE - INTERVAL '30 days'
        ) AS downtime_hours_30d,
        -- Recent defect rate (last 30 days)
        (SELECT ROUND(SUM(qi.qty_defective)::NUMERIC
                 / NULLIF(SUM(qi.qty_inspected), 0) * 100, 4)
         FROM quality_inspections qi
         WHERE qi.machine_id = m.machine_id
           AND qi.inspection_date >= CURRENT_DATE - INTERVAL '30 days'
        ) AS defect_rate_30d,
        -- Overdue maintenance count
        (SELECT COUNT(*)
         FROM maintenance mt
         WHERE mt.machine_id = m.machine_id
           AND NOT mt.is_completed
           AND mt.start_datetime < NOW()
        ) AS overdue_maintenance
    FROM machines m
    JOIN plants   pl ON pl.plant_id = m.plant_id
)
SELECT *,
    CASE
        WHEN overdue_maintenance > 0      THEN 'CRITICAL'
        WHEN days_since_maintenance > 90  THEN 'HIGH'
        WHEN downtime_hours_30d > 50      THEN 'MEDIUM'
        WHEN defect_rate_30d > 5          THEN 'MEDIUM'
        ELSE 'LOW'
    END AS alert_level
FROM machine_kpis
WHERE
    overdue_maintenance > 0
    OR days_since_maintenance > 60
    OR downtime_hours_30d > 30
    OR defect_rate_30d > 5
ORDER BY
    CASE WHEN overdue_maintenance > 0 THEN 0
         WHEN days_since_maintenance > 90 THEN 1
         ELSE 2 END,
    downtime_hours_30d DESC NULLS LAST;


-- ============================================================
-- QUERY 7: Inventory Reorder Alert with Days-of-Stock
-- ============================================================
WITH daily_consumption AS (
    SELECT
        product_id,
        -- Average daily OUT quantity over last 90 days
        ROUND(
            SUM(quantity) FILTER (WHERE transaction_type = 'OUT')::NUMERIC
            / 90, 2
        ) AS avg_daily_consumption
    FROM inventory
    WHERE transaction_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY product_id
),
latest_stock AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        current_stock,
        reorder_level
    FROM inventory
    ORDER BY product_id, transaction_time DESC
)
SELECT
    p.product_id,
    p.product_name,
    p.product_code,
    p.category,
    ls.current_stock,
    ls.reorder_level,
    p.reorder_quantity,
    dc.avg_daily_consumption,
    CASE
        WHEN dc.avg_daily_consumption > 0
        THEN ROUND(ls.current_stock / dc.avg_daily_consumption, 1)
        ELSE NULL
    END                         AS days_of_stock,
    ROUND(ls.current_stock * p.unit_cost, 2) AS stock_value,
    CASE
        WHEN ls.current_stock = 0                       THEN 'OUT OF STOCK'
        WHEN ls.current_stock <= ls.reorder_level       THEN 'REORDER NOW'
        WHEN ls.current_stock <= ls.reorder_level * 1.2 THEN 'REORDER SOON'
        ELSE 'OK'
    END                         AS reorder_status
FROM products       p
JOIN latest_stock   ls ON ls.product_id = p.product_id
LEFT JOIN daily_consumption dc ON dc.product_id = p.product_id
WHERE p.is_active = TRUE
ORDER BY
    CASE WHEN ls.current_stock = 0                      THEN 0
         WHEN ls.current_stock <= ls.reorder_level      THEN 1
         WHEN ls.current_stock <= ls.reorder_level * 1.2 THEN 2
         ELSE 3 END,
    days_of_stock NULLS FIRST;


-- ============================================================
-- QUERY 8: Conditional Aggregation — Defects by Severity per Plant
-- ============================================================
SELECT
    pl.plant_name,
    COUNT(d.defect_id)                                          AS total_defects,
    COUNT(*) FILTER (WHERE d.severity = 'Low')                  AS low_severity,
    COUNT(*) FILTER (WHERE d.severity = 'Medium')               AS medium_severity,
    COUNT(*) FILTER (WHERE d.severity = 'High')                 AS high_severity,
    COUNT(*) FILTER (WHERE d.severity = 'Critical')             AS critical_severity,
    COUNT(*) FILTER (WHERE d.is_resolved)                       AS resolved,
    COUNT(*) FILTER (WHERE NOT d.is_resolved)                   AS open,
    ROUND(
        COUNT(*) FILTER (WHERE d.is_resolved)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                           AS resolution_rate_pct
FROM defects d
JOIN plants  pl ON pl.plant_id = d.plant_id
GROUP BY pl.plant_name
ORDER BY total_defects DESC;


-- ============================================================
-- QUERY 9: ROW_NUMBER — Latest Maintenance per Machine
-- ============================================================
WITH ranked_maintenance AS (
    SELECT
        mt.*,
        m.machine_name,
        pl.plant_name,
        ROW_NUMBER() OVER (
            PARTITION BY mt.machine_id
            ORDER BY mt.start_datetime DESC
        ) AS rn
    FROM maintenance mt
    JOIN machines m  ON m.machine_id  = mt.machine_id
    JOIN plants   pl ON pl.plant_id   = mt.plant_id
)
SELECT
    machine_id,
    machine_name,
    plant_name,
    maintenance_type,
    description,
    technician_name,
    start_datetime,
    end_datetime,
    duration_hours,
    cost,
    is_completed,
    parts_replaced
FROM ranked_maintenance
WHERE rn = 1
ORDER BY machine_id;


-- ============================================================
-- QUERY 10: Order Delivery Performance by Customer
-- ============================================================
SELECT
    o.customer_name,
    COUNT(o.order_id)                                               AS total_orders,
    ROUND(SUM(o.total_amount), 2)                                   AS total_revenue,
    COUNT(*) FILTER (WHERE o.status = 'Completed')                  AS completed,
    COUNT(*) FILTER (WHERE o.status = 'Cancelled')                  AS cancelled,
    COUNT(*) FILTER (
        WHERE o.actual_delivery IS NOT NULL
          AND o.actual_delivery <= o.expected_delivery
    )                                                               AS on_time_deliveries,
    ROUND(
        COUNT(*) FILTER (
            WHERE o.actual_delivery IS NOT NULL
              AND o.actual_delivery <= o.expected_delivery
        )::NUMERIC
        / NULLIF(COUNT(*) FILTER (WHERE o.actual_delivery IS NOT NULL), 0) * 100, 2
    )                                                               AS on_time_pct,
    ROUND(AVG(o.actual_delivery - o.expected_delivery) FILTER (
        WHERE o.actual_delivery IS NOT NULL
    ), 1)                                                           AS avg_delivery_variance_days
FROM orders o
GROUP BY o.customer_name
HAVING COUNT(o.order_id) >= 5
ORDER BY total_revenue DESC
LIMIT 20;
