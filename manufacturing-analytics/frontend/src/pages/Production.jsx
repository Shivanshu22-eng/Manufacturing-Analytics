import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchProduction } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge, Pagination } from '../components/UI'

export default function Production() {
  const [page,   setPage]   = useState(1)
  const [filter, setFilter] = useState({ plant_id: '', status: '', date_from: '2024-01-01', date_to: '2024-12-31' })
  const params = { page, page_size: 50, ...Object.fromEntries(Object.entries(filter).filter(([,v]) => v)) }
  const { data, loading, error } = useApi(fetchProduction, params)

  const totalPages = data ? Math.ceil(data.total / 50) : 1

  return (
    <>
      <div className="section-title">Production Records</div>
      <div className="section-sub">Searchable, sortable production run history</div>

      <div className="filters-bar">
        <input className="filter-input" type="date" value={filter.date_from}
          onChange={e => { setFilter(f => ({ ...f, date_from: e.target.value })); setPage(1) }} />
        <input className="filter-input" type="date" value={filter.date_to}
          onChange={e => { setFilter(f => ({ ...f, date_to: e.target.value })); setPage(1) }} />
        <select className="filter-select" value={filter.status}
          onChange={e => { setFilter(f => ({ ...f, status: e.target.value })); setPage(1) }}>
          <option value="">All Statuses</option>
          {['Excellent','Good','Average','Poor'].map(s => <option key={s}>{s}</option>)}
        </select>
        <span className="text-muted" style={{ fontSize: 12 }}>
          {data ? `${data.total.toLocaleString()} records` : ''}
        </span>
      </div>

      <div className="card">
        {loading ? <LoadingState /> : error ? <ErrorState message={error} /> : !data?.data?.length ? <EmptyState /> : (
          <>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th><th>Plant</th><th>Machine</th><th>Product</th>
                    <th>Planned</th><th>Actual</th><th>Efficiency</th><th>Downtime</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.map(r => (
                    <tr key={r.production_id}>
                      <td>{r.production_date}</td>
                      <td style={{ maxWidth: 130, overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.plant_name}</td>
                      <td style={{ maxWidth: 130, overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.machine_name}</td>
                      <td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.product_name}</td>
                      <td>{r.planned_quantity?.toLocaleString()}</td>
                      <td>{r.actual_quantity?.toLocaleString()}</td>
                      <td>
                        <span className={r.efficiency_pct >= 90 ? 'text-success fw-700' : r.efficiency_pct >= 70 ? 'text-warning' : 'text-danger'}>
                          {r.efficiency_pct}%
                        </span>
                      </td>
                      <td>{r.downtime_minutes} min</td>
                      <td><Badge status={r.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={page} totalPages={totalPages} onPageChange={setPage} total={data.total} pageSize={50} />
          </>
        )}
      </div>
    </>
  )
}
