import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchMachines, fetchMachine, fetchDowntime } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge, KPICard } from '../components/UI'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function MachineDetail({ machineId, onClose }) {
  const { data, loading } = useApi(fetchMachine, {}, true)
  const [d, setD] = useState(null)

  // Fetch on mount when machineId changes
  const { data: detail, loading: dL, error } = useApi(
    () => fetchMachine(machineId), {}, true
  )

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,.7)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200,
    }}>
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 28, width: 540, maxHeight: '80vh', overflowY: 'auto' }}>
        <div className="flex-between" style={{ marginBottom: 20 }}>
          <h2 style={{ fontSize: 16 }}>Machine Detail</h2>
          <button className="btn btn-ghost" onClick={onClose}>✕ Close</button>
        </div>
        {dL ? <LoadingState /> : error ? <ErrorState message={error} /> : detail ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[
              ['Machine Name', detail.machine_name],
              ['Type', detail.machine_type],
              ['Plant', detail.plant_name],
              ['Status', <Badge key="s" status={detail.status} />],
              ['Hourly Capacity', `${detail.hourly_capacity} units/hr`],
              ['Installed', detail.installation_date],
              ['Last Maintenance', detail.last_maintenance_date || 'Never'],
              ['Total Shifts', detail.total_shifts?.toLocaleString()],
              ['Utilization', `${detail.utilization_pct ?? '—'}%`],
              ['Avg Efficiency', `${detail.avg_efficiency_pct ?? '—'}%`],
              ['Total Downtime', `${detail.total_downtime_hours ?? '—'} hrs`],
              ['Overdue Tasks', detail.overdue_maintenance],
            ].map(([k, v]) => (
              <div key={k} style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{k}</div>
                <div style={{ fontWeight: 600 }}>{v ?? '—'}</div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function Machines() {
  const [selectedId, setSelectedId] = useState(null)
  const { data: machines, loading, error } = useApi(fetchMachines)
  const { data: downtime } = useApi(fetchDowntime, { top_n: 10 })

  return (
    <>
      <div className="section-title">Machines</div>
      <div className="section-sub">Fleet status, utilization, and downtime analysis</div>

      {selectedId && <MachineDetail machineId={selectedId} onClose={() => setSelectedId(null)} />}

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Top 10 Machines by Downtime</div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={downtime || []} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis type="category" dataKey="machine_name" tick={{ fill: '#8b949e', fontSize: 10 }} width={140} />
            <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} />
            <Bar dataKey="downtime_hours" name="Downtime (hrs)" fill="#ef4444" radius={[0,4,4,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">All Machines</div>
          <div className="card-subtitle">Click a row to see detail</div>
        </div>
        {loading ? <LoadingState /> : error ? <ErrorState message={error} /> : !machines?.length ? <EmptyState /> : (
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th><th>Machine</th><th>Type</th><th>Plant</th>
                  <th>Capacity</th><th>Status</th><th>Last Maintenance</th>
                </tr>
              </thead>
              <tbody>
                {machines.map(m => (
                  <tr key={m.machine_id} style={{ cursor: 'pointer' }} onClick={() => setSelectedId(m.machine_id)}>
                    <td style={{ color: 'var(--accent-light)', fontWeight: 600 }}>#{m.machine_id}</td>
                    <td>{m.machine_name}</td>
                    <td>{m.machine_type}</td>
                    <td style={{ maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis' }}>{m.plant_name}</td>
                    <td>{m.hourly_capacity} u/hr</td>
                    <td>
                      <span className={`status-dot ${m.status?.toLowerCase().replace(' ','')}`} />
                      <Badge status={m.status} />
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{m.last_maintenance_date || 'Never'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}
