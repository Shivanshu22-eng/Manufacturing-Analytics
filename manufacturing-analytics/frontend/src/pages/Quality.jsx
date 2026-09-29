import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchDefectSummary, fetchDefectTrend, fetchTopDefMachines, fetchDefects } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge, Pagination } from '../components/UI'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const COLORS = ['#ef4444','#f59e0b','#3b82f6','#8b5cf6','#22c55e','#06b6d4','#f97316']

export default function Quality() {
  const [page,   setPage]   = useState(1)
  const [filter, setFilter] = useState({ severity: '', is_resolved: '' })

  const params = {
    page, page_size: 50,
    ...Object.fromEntries(Object.entries(filter).filter(([, v]) => v !== '')),
  }

  const { data: defects,  loading: dL, error: dE } = useApi(fetchDefects, params)
  const { data: summary,  loading: sL }             = useApi(fetchDefectSummary)
  const { data: trend,    loading: tL }             = useApi(fetchDefectTrend, { granularity: 'monthly' })
  const { data: topMach,  loading: mL }             = useApi(fetchTopDefMachines, { top_n: 8 })

  const totalPages = defects ? Math.ceil(defects.total / 50) : 1

  return (
    <>
      <div className="section-title">Quality Control</div>
      <div className="section-sub">Defect tracking, trend analysis, and machine quality ranking</div>

      {/* Top row charts */}
      <div className="charts-grid" style={{ marginBottom: 20 }}>
        {/* Defect trend */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Monthly Defect Count Trend</div>
          </div>
          {tL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trend || []} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="period" tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => v?.slice(0, 7)} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} labelStyle={{ color: '#e6edf3' }} />
                <Line type="monotone" dataKey="defect_count" name="Defects" stroke="#ef4444" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="qty_defective" name="Qty Defective" stroke="#f59e0b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Defect category pie */}
        <div className="card">
          <div className="card-header"><div className="card-title">Defects by Category</div></div>
          {sL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={summary || []} dataKey="count" nameKey="defect_category"
                  cx="50%" cy="50%" outerRadius={85} label={({ pct_of_total }) => `${pct_of_total}%`} labelLine={false}>
                  {(summary || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: '#8b949e' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Top defective machines */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><div className="card-title">Top Machines by Defect Count</div></div>
        {mL ? <LoadingState /> : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={topMach || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} />
              <YAxis type="category" dataKey="machine_name" tick={{ fill: '#8b949e', fontSize: 10 }} width={140} />
              <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} />
              <Bar dataKey="defect_count" name="Defect Count" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Defects table */}
      <div className="card">
        <div className="card-header"><div className="card-title">Defect Log</div></div>
        <div className="filters-bar">
          <select className="filter-select" value={filter.severity}
            onChange={e => { setFilter(f => ({ ...f, severity: e.target.value })); setPage(1) }}>
            <option value="">All Severities</option>
            {['Low', 'Medium', 'High', 'Critical'].map(s => <option key={s}>{s}</option>)}
          </select>
          <select className="filter-select" value={filter.is_resolved}
            onChange={e => { setFilter(f => ({ ...f, is_resolved: e.target.value })); setPage(1) }}>
            <option value="">All States</option>
            <option value="false">Unresolved</option>
            <option value="true">Resolved</option>
          </select>
          <span className="text-muted" style={{ fontSize: 12 }}>
            {defects ? `${defects.total.toLocaleString()} defects` : ''}
          </span>
        </div>

        {dL ? <LoadingState /> : dE ? <ErrorState message={dE} /> : !defects?.data?.length ? <EmptyState /> : (
          <>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th><th>Product</th><th>Category</th><th>Description</th>
                    <th>Severity</th><th>Qty</th><th>Resolved</th>
                  </tr>
                </thead>
                <tbody>
                  {defects.data.map(d => (
                    <tr key={d.defect_id}>
                      <td>{d.defect_date}</td>
                      <td style={{ maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.product_name}</td>
                      <td>{d.defect_category}</td>
                      <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-secondary)' }}>{d.defect_description}</td>
                      <td><Badge status={d.severity} /></td>
                      <td>{d.qty_defective}</td>
                      <td>{d.is_resolved
                        ? <span className="badge badge-success">✓ Yes</span>
                        : <span className="badge badge-warning">Pending</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={page} totalPages={totalPages} onPageChange={setPage} total={defects.total} pageSize={50} />
          </>
        )}
      </div>
    </>
  )
}
