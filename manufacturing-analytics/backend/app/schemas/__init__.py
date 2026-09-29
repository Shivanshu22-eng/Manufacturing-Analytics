"""
Pydantic response schemas for all API endpoints.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ─── Shared ────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list


# ─── Plants ─────────────────────────────────────────────────────────────────

class PlantOut(BaseModel):
    plant_id: int
    plant_name: str
    city: str
    state: str
    country: str
    capacity: int
    established_year: int
    is_active: bool

    class Config:
        from_attributes = True


# ─── Machines ────────────────────────────────────────────────────────────────

class MachineOut(BaseModel):
    machine_id: int
    machine_name: str
    machine_type: str
    plant_id: int
    plant_name: Optional[str] = None
    model_number: str
    manufacturer: str
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    status: str
    hourly_capacity: int

    class Config:
        from_attributes = True


class MachineDetailOut(MachineOut):
    total_shifts: Optional[int] = None
    total_downtime_hours: Optional[float] = None
    utilization_pct: Optional[float] = None
    avg_efficiency_pct: Optional[float] = None
    total_produced: Optional[int] = None
    overdue_maintenance: Optional[int] = None


# ─── Products ────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    product_id: int
    product_name: str
    product_code: str
    category: str
    unit_of_measure: str
    unit_cost: float
    selling_price: float
    reorder_level: int
    reorder_quantity: int
    is_active: bool

    class Config:
        from_attributes = True


# ─── Production ──────────────────────────────────────────────────────────────

class ProductionOut(BaseModel):
    production_id: int
    machine_id: int
    machine_name: Optional[str] = None
    plant_id: int
    plant_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    production_date: date
    shift_duration_min: int
    planned_quantity: int
    actual_quantity: int
    efficiency_pct: float
    downtime_minutes: int
    status: str

    class Config:
        from_attributes = True


class ProductionTrendPoint(BaseModel):
    period: str
    total_planned: int
    total_actual: int
    efficiency_pct: float
    total_downtime_hours: float
    shifts: int


# ─── Quality ─────────────────────────────────────────────────────────────────

class QualityOut(BaseModel):
    inspection_id: int
    production_id: int
    machine_id: int
    plant_id: int
    product_id: int
    product_name: Optional[str] = None
    inspection_date: date
    inspector_name: str
    qty_inspected: int
    qty_passed: int
    qty_defective: int
    defect_rate_pct: float
    result: str

    class Config:
        from_attributes = True


class DefectOut(BaseModel):
    defect_id: int
    inspection_id: int
    machine_id: int
    plant_id: int
    product_id: int
    product_name: Optional[str] = None
    defect_category: str
    defect_description: str
    severity: str
    qty_defective: int
    defect_date: date
    is_resolved: bool

    class Config:
        from_attributes = True


class DefectSummary(BaseModel):
    defect_category: str
    count: int
    qty_defective: int
    pct_of_total: float


# ─── Maintenance ─────────────────────────────────────────────────────────────

class MaintenanceOut(BaseModel):
    maintenance_id: int
    machine_id: int
    machine_name: Optional[str] = None
    plant_id: int
    plant_name: Optional[str] = None
    maintenance_type: str
    description: str
    technician_name: str
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    duration_hours: Optional[float] = None
    cost: float
    is_completed: bool
    parts_replaced: str

    class Config:
        from_attributes = True


# ─── Inventory ───────────────────────────────────────────────────────────────

class InventoryOut(BaseModel):
    transaction_id: int
    product_id: int
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    category: Optional[str] = None
    transaction_type: str
    quantity: int
    transaction_date: date
    unit_cost: float
    current_stock: int
    reorder_level: int
    is_below_reorder: bool

    class Config:
        from_attributes = True


class InventoryStatusOut(BaseModel):
    product_id: int
    product_name: str
    product_code: str
    category: str
    current_stock: int
    reorder_level: int
    reorder_quantity: int
    is_below_reorder: bool
    stock_value: float
    stock_status: str
    last_transaction_date: Optional[date] = None


# ─── Orders ──────────────────────────────────────────────────────────────────

class OrderOut(BaseModel):
    order_id: int
    order_number: str
    customer_name: str
    product_id: int
    product_name: Optional[str] = None
    quantity_ordered: int
    unit_price: float
    total_amount: float
    order_date: date
    expected_delivery: date
    actual_delivery: Optional[date] = None
    status: str
    priority: str

    class Config:
        from_attributes = True


# ─── Dashboard KPIs ──────────────────────────────────────────────────────────

class DashboardKPIs(BaseModel):
    total_production_runs: int
    total_units_produced: int
    avg_efficiency_pct: float
    overall_defect_rate_pct: float
    open_defects: int
    total_machines: int
    operational_machines: int
    avg_utilization_pct: float
    total_downtime_hours: float
    low_stock_products: int
    out_of_stock: int
    overdue_maintenance: int
    active_orders: int
    revenue: float


# ─── Alerts ──────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    alert_id: str
    alert_type: str
    severity: str           # critical / high / medium / low
    title: str
    message: str
    affected_entity: str
    entity_id: int
    entity_name: str
    plant_name: Optional[str] = None
    timestamp: datetime
    is_active: bool
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
