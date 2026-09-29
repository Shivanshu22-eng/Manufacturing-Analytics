import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
})

// ── Dashboard ─────────────────────────────────────────────────────────────
export const fetchKPIs        = (params = {}) => api.get('/api/dashboard/kpis', { params }).then(r => r.data)
export const fetchProdTrend   = (params = {}) => api.get('/api/dashboard/production-trend', { params }).then(r => r.data)

// ── Production ────────────────────────────────────────────────────────────
export const fetchProduction  = (params = {}) => api.get('/api/production', { params }).then(r => r.data)
export const fetchProdByPlant = (params = {}) => api.get('/api/production/by-plant', { params }).then(r => r.data)

// ── Machines ──────────────────────────────────────────────────────────────
export const fetchMachines    = (params = {}) => api.get('/api/machines', { params }).then(r => r.data)
export const fetchMachine     = (id)          => api.get(`/api/machines/${id}`).then(r => r.data)
export const fetchDowntime    = (params = {}) => api.get('/api/machines/downtime', { params }).then(r => r.data)

// ── Quality ───────────────────────────────────────────────────────────────
export const fetchInspections     = (params = {}) => api.get('/api/quality/inspections', { params }).then(r => r.data)
export const fetchDefects         = (params = {}) => api.get('/api/quality/defects', { params }).then(r => r.data)
export const fetchDefectSummary   = (params = {}) => api.get('/api/quality/defect-summary', { params }).then(r => r.data)
export const fetchDefectTrend     = (params = {}) => api.get('/api/quality/defect-trend', { params }).then(r => r.data)
export const fetchTopDefMachines  = (params = {}) => api.get('/api/quality/top-defective-machines', { params }).then(r => r.data)

// ── Maintenance ───────────────────────────────────────────────────────────
export const fetchMaintenance = (params = {}) => api.get('/api/maintenance', { params }).then(r => r.data)
export const fetchOverdue     = ()             => api.get('/api/maintenance/overdue').then(r => r.data)
export const fetchUpcoming    = ()             => api.get('/api/maintenance/upcoming').then(r => r.data)

// ── Inventory ─────────────────────────────────────────────────────────────
export const fetchInventoryStatus = ()             => api.get('/api/inventory/status').then(r => r.data)
export const fetchInventory       = (params = {})  => api.get('/api/inventory', { params }).then(r => r.data)
export const fetchInventoryTrend  = (params = {})  => api.get('/api/inventory/trend', { params }).then(r => r.data)

// ── Orders ────────────────────────────────────────────────────────────────
export const fetchOrders = (params = {}) => api.get('/api/orders', { params }).then(r => r.data)

// ── Alerts ────────────────────────────────────────────────────────────────
export const fetchAlerts = () => api.get('/api/alerts').then(r => r.data)
