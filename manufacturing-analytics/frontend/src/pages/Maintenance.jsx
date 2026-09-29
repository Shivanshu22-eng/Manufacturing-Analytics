import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchMaintenance, fetchOverdue, fetchUpcoming } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge, Pagination } from '../components/UI'

export default function Maintenance() {
  const [tab,    setTab]    = useState('all')   // all | overdue | upcoming
  const [page,   setPage]   = useState(1)
  const [filter, setFilter] = useState({ maintenance_type: '', is_completed: '' })

  const params = {
    page, page_size: 50,
    ...Object.fromEntries(Object.entries(filter).filter(([, v]) => v !== '')),
  }

  const { data: all,      loading: aL, error: aE } = useApi(fetchMaintenance, params, tab === 'all')
  const { data: overdue,  loading: oL, error: oE } = useApi(fetchOverdue,    {},      tab === 'overdue')
  const { data: upcoming, loading: uL, error: uE } = useApi(fetchUpcoming,   {},      tab === 'upcoming')

  const totalPages = all ? Math.ceil(all.total / 50) : 1

  const TableHead = () => (
    <tr>
      <th>Start Date</th><th>Machine</th><th>Plant</th><th>Type</th>
      <th>Technician</th><th>Duration</th><th>Cost (₹)</th><th>Status</th>
    </tr>
  )

  const TableRow = ({ r }) => (
    <tr key={r.maintenance_id}>
      <td>{r.start_datetime ? new Date(r.start_datetime).toLocaleDateString('en-IN') : '—'}</td>
      <td>{r.machine_name}</td>
      <td style={{ maxWidth: 130, overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.plant_name}</td>
      <td>{r.maintenance_type}</td>
      <td style={{ color: 'var(--text-secondary)' }}>{r.technician_name}</td>
      <td>{r.duration_hours != null ? `${r.duration_hours}h` : '—'}</td>
      <td>₹{Number(r.cost || 0).toLocaleString('en-IN')}</td>
      <td>{r.is_completed
        ? <span className="badge badge-success">✓ Done</span>
        : <span className="badge badge-warning">Pending</span>}
      </td>
    </tr>
  )

  const activeData = tab === 'all' ? all?.data : tab === 'overdue' ? overdue : upcoming
  const activeLoad = tab === 'all' ? aL : tab === 'overdue' ? oL : uL
  const activeErr  = tab === 'all' ? aE : tab === 'overdue' ? oE : uE

  return (
    <>
      <div className="section-title">Maintenance</div>
      <div className="section-sub">Scheduled, overdue, and upcoming machine maintenance records</div>

      {/* Summary pills */}
      <div className="filters-bar" style={{ marginBottom: 16 }}>
        {['all','overdue','upcoming'].map(t => (
          <button key={t} className={`btn ${tab === t ? '' : 'btn-ghost'}`}
            onClick={() => { setTab(t); setPage(1) }}
            style={{ textTransform: 'capitalize' }}>
            {t === 'overdue' ? '🔴 Overdue' : t === 'upcoming' ? '🟡 Upcoming (30d)' : '📋 All Records'}
          </button>
        ))}
      </div>

      {tab === 'all' && (
        <div className="filters-bar">
          <select className="filter-select" value={filter.maintenance_type}
            onChange={e => { setFilter(f => ({ ...f, maintenance_type: e.target.value })); setPage(1) }}>
            <option value="">All Types</option>
            {['Preventive','Corrective','Predictive','Emergency'].map(t => <option key={t}>{t}</option>)}
          </select>
          <select className="filter-select" value={filter.is_completed}
            onChange={e => { setFilter(f => ({ ...f, is_completed: e.target.value })); setPage(1) }}>
            <option value="">All States</option>
            <option value="false">Pending</option>
            <option value="true">Completed</option>
          </select>
          <span className="text-muted" style={{ fontSize: 12 }}>{all ? `${all.total.toLocaleString()} records` : ''}</span>
        </div>
      )}

      <div className="card">
        {activeLoad ? <LoadingState /> : activeErr ? <ErrorState message={activeErr} /> : !activeData?.length ? <EmptyState /> : (
          <>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead><TableHead /></thead>
                <tbody>
                  {activeData.map(r => <TableRow key={r.maintenance_id} r={r} />)}
                </tbody>
              </table>
            </div>
            {tab === 'all' && <Pagination page={page} totalPages={totalPages} onPageChange={setPage} total={all.total} pageSize={50} />}
          </>
        )}
      </div>
    </>
  )
}
