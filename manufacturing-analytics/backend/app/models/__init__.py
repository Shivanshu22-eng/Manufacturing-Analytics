"""
SQLAlchemy ORM Models — mirror the PostgreSQL schema exactly.
"""
from sqlalchemy import (
    BigInteger, Boolean, Column, Date, Integer, Numeric,
    SmallInteger, String, Text, TIMESTAMP, ForeignKey,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Plant(Base):
    __tablename__ = "plants"

    plant_id         = Column(Integer,     primary_key=True, index=True)
    plant_name       = Column(String(120), nullable=False)
    city             = Column(String(80),  nullable=False)
    state            = Column(String(80),  nullable=False)
    country          = Column(String(60),  nullable=False, default="India")
    capacity         = Column(Integer,     nullable=False)
    established_year = Column(SmallInteger,nullable=False)
    is_active        = Column(Boolean,     nullable=False, default=True)
    created_at       = Column(TIMESTAMP(timezone=True))

    machines    = relationship("Machine",    back_populates="plant")
    production  = relationship("Production", back_populates="plant")
    maintenance = relationship("Maintenance",back_populates="plant")


class Machine(Base):
    __tablename__ = "machines"

    machine_id            = Column(Integer,     primary_key=True, index=True)
    machine_name          = Column(String(120), nullable=False)
    machine_type          = Column(String(80),  nullable=False)
    plant_id              = Column(Integer,     ForeignKey("plants.plant_id"), nullable=False)
    model_number          = Column(String(40),  nullable=False)
    manufacturer          = Column(String(120), nullable=False)
    installation_date     = Column(Date)
    last_maintenance_date = Column(Date)
    status                = Column(String(30),  nullable=False, default="Operational")
    hourly_capacity       = Column(Integer,     nullable=False)
    created_at            = Column(TIMESTAMP(timezone=True))

    plant       = relationship("Plant",      back_populates="machines")
    production  = relationship("Production", back_populates="machine")
    maintenance = relationship("Maintenance",back_populates="machine")


class Product(Base):
    __tablename__ = "products"

    product_id       = Column(Integer,     primary_key=True, index=True)
    product_name     = Column(String(200), nullable=False)
    product_code     = Column(String(20),  nullable=False, unique=True)
    category         = Column(String(80),  nullable=False)
    unit_of_measure  = Column(String(20),  nullable=False, default="Piece")
    unit_cost        = Column(Numeric(12,2),nullable=False)
    selling_price    = Column(Numeric(12,2),nullable=False)
    reorder_level    = Column(Integer,     nullable=False)
    reorder_quantity = Column(Integer,     nullable=False)
    weight_kg        = Column(Numeric(8,3),nullable=False)
    is_active        = Column(Boolean,     nullable=False, default=True)
    created_at       = Column(TIMESTAMP(timezone=True))

    production = relationship("Production",         back_populates="product")
    inventory  = relationship("Inventory",          back_populates="product")
    orders     = relationship("Order",              back_populates="product")


class Production(Base):
    __tablename__ = "production"

    production_id      = Column(BigInteger,  primary_key=True, index=True)
    machine_id         = Column(Integer,     ForeignKey("machines.machine_id"), nullable=False)
    plant_id           = Column(Integer,     ForeignKey("plants.plant_id"),     nullable=False)
    product_id         = Column(Integer,     ForeignKey("products.product_id"), nullable=False)
    production_date    = Column(Date,        nullable=False)
    shift_start        = Column(TIMESTAMP(timezone=True))
    shift_duration_min = Column(Integer,     nullable=False)
    planned_quantity   = Column(Integer,     nullable=False)
    actual_quantity    = Column(Integer,     nullable=False)
    efficiency_pct     = Column(Numeric(6,2),nullable=False)
    downtime_minutes   = Column(Integer,     nullable=False, default=0)
    status             = Column(String(20),  nullable=False)
    created_at         = Column(TIMESTAMP(timezone=True))

    plant   = relationship("Plant",   back_populates="production")
    machine = relationship("Machine", back_populates="production")
    product = relationship("Product", back_populates="production")
    quality_inspections = relationship("QualityInspection", back_populates="production")


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    inspection_id    = Column(BigInteger,   primary_key=True, index=True)
    production_id    = Column(BigInteger,   ForeignKey("production.production_id"), nullable=False)
    machine_id       = Column(Integer,      ForeignKey("machines.machine_id"),       nullable=False)
    plant_id         = Column(Integer,      ForeignKey("plants.plant_id"),           nullable=False)
    product_id       = Column(Integer,      ForeignKey("products.product_id"),       nullable=False)
    inspection_date  = Column(Date,         nullable=False)
    inspection_time  = Column(TIMESTAMP(timezone=True))
    inspector_name   = Column(String(120),  nullable=False)
    qty_inspected    = Column(Integer,      nullable=False)
    qty_passed       = Column(Integer,      nullable=False)
    qty_defective    = Column(Integer,      nullable=False)
    defect_rate_pct  = Column(Numeric(7,4), nullable=False)
    result           = Column(String(10),   nullable=False)
    notes            = Column(Text,         nullable=False, default="")
    created_at       = Column(TIMESTAMP(timezone=True))

    production = relationship("Production", back_populates="quality_inspections")
    defects    = relationship("Defect",     back_populates="inspection")


class Defect(Base):
    __tablename__ = "defects"

    defect_id           = Column(BigInteger,  primary_key=True, index=True)
    inspection_id       = Column(BigInteger,  ForeignKey("quality_inspections.inspection_id"), nullable=False)
    production_id       = Column(BigInteger,  ForeignKey("production.production_id"),          nullable=False)
    machine_id          = Column(Integer,     ForeignKey("machines.machine_id"),               nullable=False)
    plant_id            = Column(Integer,     ForeignKey("plants.plant_id"),                   nullable=False)
    product_id          = Column(Integer,     ForeignKey("products.product_id"),               nullable=False)
    defect_category     = Column(String(60),  nullable=False)
    defect_description  = Column(String(200), nullable=False)
    severity            = Column(String(20),  nullable=False)
    qty_defective       = Column(Integer,     nullable=False)
    defect_date         = Column(Date,        nullable=False)
    is_resolved         = Column(Boolean,     nullable=False, default=False)
    resolution_notes    = Column(Text,        nullable=False, default="")
    created_at          = Column(TIMESTAMP(timezone=True))

    inspection = relationship("QualityInspection", back_populates="defects")


class Maintenance(Base):
    __tablename__ = "maintenance"

    maintenance_id   = Column(BigInteger,   primary_key=True, index=True)
    machine_id       = Column(Integer,      ForeignKey("machines.machine_id"), nullable=False)
    plant_id         = Column(Integer,      ForeignKey("plants.plant_id"),     nullable=False)
    maintenance_type = Column(String(60),   nullable=False)
    description      = Column(String(200),  nullable=False)
    technician_name  = Column(String(120),  nullable=False)
    start_datetime   = Column(TIMESTAMP(timezone=True), nullable=False)
    end_datetime     = Column(TIMESTAMP(timezone=True))
    duration_hours   = Column(Numeric(6,2))
    cost             = Column(Numeric(12,2),nullable=False)
    is_completed     = Column(Boolean,      nullable=False, default=False)
    parts_replaced   = Column(String(100),  nullable=False, default="None")
    created_at       = Column(TIMESTAMP(timezone=True))

    machine = relationship("Machine", back_populates="maintenance")
    plant   = relationship("Plant",   back_populates="maintenance")


class Inventory(Base):
    __tablename__ = "inventory"

    transaction_id   = Column(BigInteger,   primary_key=True, index=True)
    product_id       = Column(Integer,      ForeignKey("products.product_id"), nullable=False)
    transaction_type = Column(String(20),   nullable=False)
    quantity         = Column(Integer,      nullable=False)
    transaction_date = Column(Date,         nullable=False)
    transaction_time = Column(TIMESTAMP(timezone=True))
    unit_cost        = Column(Numeric(12,2),nullable=False)
    reference_doc    = Column(String(40),   nullable=False, default="")
    notes            = Column(Text,         nullable=False, default="")
    current_stock    = Column(Integer,      nullable=False)
    reorder_level    = Column(Integer,      nullable=False)
    is_below_reorder = Column(Boolean,      nullable=False, default=False)
    created_at       = Column(TIMESTAMP(timezone=True))

    product = relationship("Product", back_populates="inventory")


class Order(Base):
    __tablename__ = "orders"

    order_id          = Column(BigInteger,   primary_key=True, index=True)
    order_number      = Column(String(30),   nullable=False, unique=True)
    customer_name     = Column(String(200),  nullable=False)
    product_id        = Column(Integer,      ForeignKey("products.product_id"), nullable=False)
    quantity_ordered  = Column(Integer,      nullable=False)
    unit_price        = Column(Numeric(12,2),nullable=False)
    total_amount      = Column(Numeric(15,2),nullable=False)
    order_date        = Column(Date,         nullable=False)
    expected_delivery = Column(Date,         nullable=False)
    actual_delivery   = Column(Date)
    status            = Column(String(20),   nullable=False)
    priority          = Column(String(10),   nullable=False)
    notes             = Column(Text,         nullable=False, default="")
    created_at        = Column(TIMESTAMP(timezone=True))

    product = relationship("Product", back_populates="orders")
