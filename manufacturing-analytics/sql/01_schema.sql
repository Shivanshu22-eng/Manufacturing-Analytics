-- =============================================================================
-- Manufacturing Intelligence & Operations Analytics Platform
-- Phase 2: PostgreSQL Schema
-- File: sql/01_schema.sql
-- =============================================================================

-- Drop in reverse-dependency order (safe re-run)
DROP TABLE IF EXISTS defects              CASCADE;
DROP TABLE IF EXISTS quality_inspections  CASCADE;
DROP TABLE IF EXISTS production           CASCADE;
DROP TABLE IF EXISTS maintenance          CASCADE;
DROP TABLE IF EXISTS inventory            CASCADE;
DROP TABLE IF EXISTS orders               CASCADE;
DROP TABLE IF EXISTS machines             CASCADE;
DROP TABLE IF EXISTS products             CASCADE;
DROP TABLE IF EXISTS plants               CASCADE;

-- ---------------------------------------------------------------------------
-- PLANTS
-- ---------------------------------------------------------------------------
CREATE TABLE plants (
    plant_id         SERIAL          PRIMARY KEY,
    plant_name       VARCHAR(120)    NOT NULL,
    city             VARCHAR(80)     NOT NULL,
    state            VARCHAR(80)     NOT NULL,
    country          VARCHAR(60)     NOT NULL DEFAULT 'India',
    capacity         INTEGER         NOT NULL CHECK (capacity > 0),
    established_year SMALLINT        NOT NULL CHECK (established_year BETWEEN 1900 AND 2100),
    is_active        BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- MACHINES
-- ---------------------------------------------------------------------------
CREATE TABLE machines (
    machine_id            SERIAL          PRIMARY KEY,
    machine_name          VARCHAR(120)    NOT NULL,
    machine_type          VARCHAR(80)     NOT NULL,
    plant_id              INTEGER         NOT NULL REFERENCES plants(plant_id),
    model_number          VARCHAR(40)     NOT NULL,
    manufacturer          VARCHAR(120)    NOT NULL,
    installation_date     DATE            NOT NULL,
    last_maintenance_date DATE,
    status                VARCHAR(30)     NOT NULL DEFAULT 'Operational'
                          CHECK (status IN ('Operational','Under Maintenance','Idle','Decommissioned')),
    hourly_capacity       INTEGER         NOT NULL CHECK (hourly_capacity > 0),
    created_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- PRODUCTS
-- ---------------------------------------------------------------------------
CREATE TABLE products (
    product_id       SERIAL           PRIMARY KEY,
    product_name     VARCHAR(200)     NOT NULL,
    product_code     VARCHAR(20)      NOT NULL UNIQUE,
    category         VARCHAR(80)      NOT NULL,
    unit_of_measure  VARCHAR(20)      NOT NULL DEFAULT 'Piece',
    unit_cost        NUMERIC(12,2)    NOT NULL CHECK (unit_cost >= 0),
    selling_price    NUMERIC(12,2)    NOT NULL CHECK (selling_price >= 0),
    reorder_level    INTEGER          NOT NULL CHECK (reorder_level >= 0),
    reorder_quantity INTEGER          NOT NULL CHECK (reorder_quantity > 0),
    weight_kg        NUMERIC(8,3)     NOT NULL CHECK (weight_kg > 0),
    is_active        BOOLEAN          NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- PRODUCTION
-- ---------------------------------------------------------------------------
CREATE TABLE production (
    production_id      BIGSERIAL        PRIMARY KEY,
    machine_id         INTEGER          NOT NULL REFERENCES machines(machine_id),
    plant_id           INTEGER          NOT NULL REFERENCES plants(plant_id),
    product_id         INTEGER          NOT NULL REFERENCES products(product_id),
    production_date    DATE             NOT NULL,
    shift_start        TIMESTAMPTZ      NOT NULL,
    shift_duration_min INTEGER          NOT NULL CHECK (shift_duration_min > 0),
    planned_quantity   INTEGER          NOT NULL CHECK (planned_quantity > 0),
    actual_quantity    INTEGER          NOT NULL CHECK (actual_quantity >= 0),
    efficiency_pct     NUMERIC(6,2)     NOT NULL CHECK (efficiency_pct >= 0),
    downtime_minutes   INTEGER          NOT NULL DEFAULT 0 CHECK (downtime_minutes >= 0),
    status             VARCHAR(20)      NOT NULL
                       CHECK (status IN ('Excellent','Good','Average','Poor')),
    created_at         TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- QUALITY INSPECTIONS
-- ---------------------------------------------------------------------------
CREATE TABLE quality_inspections (
    inspection_id    BIGSERIAL       PRIMARY KEY,
    production_id    BIGINT          NOT NULL REFERENCES production(production_id),
    machine_id       INTEGER         NOT NULL REFERENCES machines(machine_id),
    plant_id         INTEGER         NOT NULL REFERENCES plants(plant_id),
    product_id       INTEGER         NOT NULL REFERENCES products(product_id),
    inspection_date  DATE            NOT NULL,
    inspection_time  TIMESTAMPTZ     NOT NULL,
    inspector_name   VARCHAR(120)    NOT NULL,
    qty_inspected    INTEGER         NOT NULL CHECK (qty_inspected > 0),
    qty_passed       INTEGER         NOT NULL CHECK (qty_passed >= 0),
    qty_defective    INTEGER         NOT NULL CHECK (qty_defective >= 0),
    defect_rate_pct  NUMERIC(7,4)    NOT NULL CHECK (defect_rate_pct >= 0),
    result           VARCHAR(10)     NOT NULL CHECK (result IN ('Passed','Failed')),
    notes            TEXT            NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_qi_quantities CHECK (qty_passed + qty_defective = qty_inspected)
);

-- ---------------------------------------------------------------------------
-- DEFECTS
-- ---------------------------------------------------------------------------
CREATE TABLE defects (
    defect_id           BIGSERIAL       PRIMARY KEY,
    inspection_id       BIGINT          NOT NULL REFERENCES quality_inspections(inspection_id),
    production_id       BIGINT          NOT NULL REFERENCES production(production_id),
    machine_id          INTEGER         NOT NULL REFERENCES machines(machine_id),
    plant_id            INTEGER         NOT NULL REFERENCES plants(plant_id),
    product_id          INTEGER         NOT NULL REFERENCES products(product_id),
    defect_category     VARCHAR(60)     NOT NULL,
    defect_description  VARCHAR(200)    NOT NULL,
    severity            VARCHAR(20)     NOT NULL
                        CHECK (severity IN ('Low','Medium','High','Critical')),
    qty_defective       INTEGER         NOT NULL CHECK (qty_defective > 0),
    defect_date         DATE            NOT NULL,
    is_resolved         BOOLEAN         NOT NULL DEFAULT FALSE,
    resolution_notes    TEXT            NOT NULL DEFAULT '',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- MAINTENANCE
-- ---------------------------------------------------------------------------
CREATE TABLE maintenance (
    maintenance_id   BIGSERIAL       PRIMARY KEY,
    machine_id       INTEGER         NOT NULL REFERENCES machines(machine_id),
    plant_id         INTEGER         NOT NULL REFERENCES plants(plant_id),
    maintenance_type VARCHAR(60)     NOT NULL,
    description      VARCHAR(200)    NOT NULL,
    technician_name  VARCHAR(120)    NOT NULL,
    start_datetime   TIMESTAMPTZ     NOT NULL,
    end_datetime     TIMESTAMPTZ,
    duration_hours   NUMERIC(6,2)    CHECK (duration_hours >= 0),
    cost             NUMERIC(12,2)   NOT NULL CHECK (cost >= 0),
    is_completed     BOOLEAN         NOT NULL DEFAULT FALSE,
    parts_replaced   VARCHAR(100)    NOT NULL DEFAULT 'None',
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_maint_end_after_start CHECK (end_datetime IS NULL OR end_datetime > start_datetime)
);

-- ---------------------------------------------------------------------------
-- INVENTORY
-- ---------------------------------------------------------------------------
CREATE TABLE inventory (
    transaction_id   BIGSERIAL       PRIMARY KEY,
    product_id       INTEGER         NOT NULL REFERENCES products(product_id),
    transaction_type VARCHAR(20)     NOT NULL
                     CHECK (transaction_type IN ('IN','OUT','ADJUSTMENT','RETURN','SCRAP')),
    quantity         INTEGER         NOT NULL CHECK (quantity > 0),
    transaction_date DATE            NOT NULL,
    transaction_time TIMESTAMPTZ     NOT NULL,
    unit_cost        NUMERIC(12,2)   NOT NULL CHECK (unit_cost >= 0),
    reference_doc    VARCHAR(40)     NOT NULL DEFAULT '',
    notes            TEXT            NOT NULL DEFAULT '',
    current_stock    INTEGER         NOT NULL CHECK (current_stock >= 0),
    reorder_level    INTEGER         NOT NULL CHECK (reorder_level >= 0),
    is_below_reorder BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- ORDERS
-- ---------------------------------------------------------------------------
CREATE TABLE orders (
    order_id          BIGSERIAL       PRIMARY KEY,
    order_number      VARCHAR(30)     NOT NULL UNIQUE,
    customer_name     VARCHAR(200)    NOT NULL,
    product_id        INTEGER         NOT NULL REFERENCES products(product_id),
    quantity_ordered  INTEGER         NOT NULL CHECK (quantity_ordered > 0),
    unit_price        NUMERIC(12,2)   NOT NULL CHECK (unit_price >= 0),
    total_amount      NUMERIC(15,2)   NOT NULL CHECK (total_amount >= 0),
    order_date        DATE            NOT NULL,
    expected_delivery DATE            NOT NULL,
    actual_delivery   DATE,
    status            VARCHAR(20)     NOT NULL
                      CHECK (status IN ('Pending','Confirmed','In Production','Completed','Shipped','Cancelled')),
    priority          VARCHAR(10)     NOT NULL
                      CHECK (priority IN ('Low','Normal','High','Urgent')),
    notes             TEXT            NOT NULL DEFAULT '',
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_order_delivery_after_order CHECK (expected_delivery >= order_date)
);

-- Success message
DO $$ BEGIN
    RAISE NOTICE 'Schema created successfully: 9 tables';
END $$;
