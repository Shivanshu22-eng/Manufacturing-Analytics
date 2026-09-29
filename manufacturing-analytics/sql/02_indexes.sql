-- =============================================================================
-- Phase 2: Indexes
-- File: sql/02_indexes.sql
-- Run AFTER 01_schema.sql and AFTER data is loaded (ETL phase)
-- =============================================================================

-- MACHINES
CREATE INDEX IF NOT EXISTS idx_machines_plant_id      ON machines(plant_id);
CREATE INDEX IF NOT EXISTS idx_machines_status        ON machines(status);
CREATE INDEX IF NOT EXISTS idx_machines_type          ON machines(machine_type);

-- PRODUCTION  (most-queried table)
CREATE INDEX IF NOT EXISTS idx_prod_machine_id        ON production(machine_id);
CREATE INDEX IF NOT EXISTS idx_prod_plant_id          ON production(plant_id);
CREATE INDEX IF NOT EXISTS idx_prod_product_id        ON production(product_id);
CREATE INDEX IF NOT EXISTS idx_prod_date              ON production(production_date);
CREATE INDEX IF NOT EXISTS idx_prod_status            ON production(status);
CREATE INDEX IF NOT EXISTS idx_prod_date_plant        ON production(production_date, plant_id);
CREATE INDEX IF NOT EXISTS idx_prod_date_machine      ON production(production_date, machine_id);

-- QUALITY INSPECTIONS
CREATE INDEX IF NOT EXISTS idx_qi_production_id       ON quality_inspections(production_id);
CREATE INDEX IF NOT EXISTS idx_qi_machine_id          ON quality_inspections(machine_id);
CREATE INDEX IF NOT EXISTS idx_qi_plant_id            ON quality_inspections(plant_id);
CREATE INDEX IF NOT EXISTS idx_qi_product_id          ON quality_inspections(product_id);
CREATE INDEX IF NOT EXISTS idx_qi_date                ON quality_inspections(inspection_date);
CREATE INDEX IF NOT EXISTS idx_qi_result              ON quality_inspections(result);

-- DEFECTS
CREATE INDEX IF NOT EXISTS idx_def_inspection_id      ON defects(inspection_id);
CREATE INDEX IF NOT EXISTS idx_def_machine_id         ON defects(machine_id);
CREATE INDEX IF NOT EXISTS idx_def_plant_id           ON defects(plant_id);
CREATE INDEX IF NOT EXISTS idx_def_product_id         ON defects(product_id);
CREATE INDEX IF NOT EXISTS idx_def_date               ON defects(defect_date);
CREATE INDEX IF NOT EXISTS idx_def_severity           ON defects(severity);
CREATE INDEX IF NOT EXISTS idx_def_category           ON defects(defect_category);
CREATE INDEX IF NOT EXISTS idx_def_is_resolved        ON defects(is_resolved);

-- MAINTENANCE
CREATE INDEX IF NOT EXISTS idx_maint_machine_id       ON maintenance(machine_id);
CREATE INDEX IF NOT EXISTS idx_maint_plant_id         ON maintenance(plant_id);
CREATE INDEX IF NOT EXISTS idx_maint_start            ON maintenance(start_datetime);
CREATE INDEX IF NOT EXISTS idx_maint_type             ON maintenance(maintenance_type);
CREATE INDEX IF NOT EXISTS idx_maint_completed        ON maintenance(is_completed);

-- INVENTORY
CREATE INDEX IF NOT EXISTS idx_inv_product_id         ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inv_date               ON inventory(transaction_date);
CREATE INDEX IF NOT EXISTS idx_inv_type               ON inventory(transaction_type);
CREATE INDEX IF NOT EXISTS idx_inv_below_reorder      ON inventory(is_below_reorder) WHERE is_below_reorder = TRUE;

-- ORDERS
CREATE INDEX IF NOT EXISTS idx_ord_product_id         ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_ord_date               ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_ord_status             ON orders(status);
CREATE INDEX IF NOT EXISTS idx_ord_priority           ON orders(priority);
CREATE INDEX IF NOT EXISTS idx_ord_customer           ON orders(customer_name);

DO $$ BEGIN
    RAISE NOTICE 'Indexes created successfully';
END $$;
