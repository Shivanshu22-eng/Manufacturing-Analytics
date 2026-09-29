export function LoadingState({ message = 'Loading data…' }) {
  return (
    <div className="loading-state">
      <div className="spinner" />
      <span>{message}</span>
    </div>
  )
}

export function EmptyState({ icon = '📭', message = 'No data found' }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <p>{message}</p>
    </div>
  )
}

export function ErrorState({ message }) {
  return (
    <div className="error-state">
      ⚠️ {message || 'Failed to load data. Check if the API is running.'}
    </div>
  )
}

export function KPICard({ icon, label, value, unit = '', color = 'blue', subtitle }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-value">
        {value !== null && value !== undefined
          ? typeof value === 'number'
            ? value.toLocaleString('en-IN')
            : value
          : '—'}
        {unit && <span style={{ fontSize: 16, fontWeight: 500, marginLeft: 4 }}>{unit}</span>}
      </div>
      <div className="kpi-label">{label}</div>
      {subtitle && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{subtitle}</div>}
    </div>
  )
}

export function Badge({ status }) {
  const map = {
    'Excellent':         'badge-success',
    'Good':              'badge-info',
    'Average':           'badge-warning',
    'Poor':              'badge-danger',
    'Operational':       'badge-success',
    'Under Maintenance': 'badge-warning',
    'Idle':              'badge-neutral',
    'Decommissioned':    'badge-danger',
    'Passed':            'badge-success',
    'Failed':            'badge-danger',
    'Completed':         'badge-success',
    'Shipped':           'badge-info',
    'In Production':     'badge-blue',
    'Confirmed':         'badge-blue',
    'Pending':           'badge-neutral',
    'Cancelled':         'badge-danger',
    'Low Stock':         'badge-warning',
    'Out of Stock':      'badge-danger',
    'Watch':             'badge-warning',
    'OK':                'badge-success',
    'Low':               'badge-info',
    'Medium':            'badge-warning',
    'High':              'badge-danger',
    'Critical':          'badge-critical',
    'Urgent':            'badge-danger',
    'Normal':            'badge-neutral',
  }
  return <span className={`badge ${map[status] || 'badge-neutral'}`}>{status}</span>
}

export function Pagination({ page, totalPages, onPageChange, total, pageSize }) {
  if (totalPages <= 1) return null
  return (
    <div className="pagination">
      <span className="page-info">
        {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, total)} of {total.toLocaleString()}
      </span>
      <button className="page-btn" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>← Prev</button>
      <button className="page-btn active">{page}</button>
      <button className="page-btn" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next →</button>
    </div>
  )
}
