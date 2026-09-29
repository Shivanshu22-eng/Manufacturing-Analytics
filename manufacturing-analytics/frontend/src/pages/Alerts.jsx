import { useApi } from '../hooks/useApi'
import { fetchAlerts } from '../services/api'
import { LoadingState, ErrorState, EmptyState } from '../components/UI'

const ICONS = {
  HIGH_DEFECT_RATE:    '🔬',
  HIGH_DOWNTIME:       '⏱️',
  LOW_INVENTORY:       '📦',
  OUT_OF_STOCK:        '🚫',
  OVERDUE_MAINTENANCE: '🔧',
}

const SEV_COLOR = {
  critical: 'var(--critical)',
  high:     'var(--danger)',
  medium:   'var(--warning)',
  low:      'var(--info)',
}

export default function Alerts() {
  const { data: alerts, loading, error, refetch } = useApi(fetchAlerts)

  const counts = (alerts || []).reduce((a, al) => {
    a[al.severity] = (a[al.severity] || 0) + 1; return a
  }, {})

  return (
    <>
      <div className="section-title">Operational Alerts</div>
      <div className="section-sub">Live business-rule alerts — auto-computed from production, quality, inventory, and maintenance data</div>

      {/* Severity summary */}
      <div className="kpi-grid" style={{ marginBottom: 20 }}>
        {[
          { sev: 'critical', icon: '🔴', color: 'red'    },
          { sev: 'high',     icon: '🟠', color: 'yellow' },
          { sev: 'medium',   icon: '🟡', color: 'yellow' },
          { sev: 'low',      icon: '🔵', color: 'cyan'   },
        ].map(({ sev, icon, color }) => (
          <div className={`kpi-card ${color}`} key={sev}>
            <div className="kpi-icon">{icon}</div>
            <div className="kpi-value">{counts[sev] || 0}</div>
            <div className="kpi-label" style={{ textTransform: 'capitalize' }}>{sev} Alerts</div>
          </div>
        ))}
      </div>

      <div className="flex-between" style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          {alerts?.length || 0} active alerts — sorted by severity
        </div>
        <button className="btn btn-ghost" onClick={refetch}>↻ Refresh</button>
      </div>

      {loading ? <LoadingState /> : error ? <ErrorState message={error} /> : !alerts?.length ? (
        <EmptyState icon="✅" message="No active alerts — everything looks good!" />
      ) : (
        <div className="alert-list">
          {alerts.map((a) => (
            <div key={a.alert_id} className={`alert-item ${a.severity}`}>
              <div className="alert-icon">{ICONS[a.alert_type] || '⚠️'}</div>
              <div className="alert-body">
                <div className="alert-title">{a.title}</div>
                <div className="alert-msg">{a.message}</div>
                <div className="alert-meta">
                  <span
                    className="badge"
                    style={{
                      background: `${SEV_COLOR[a.severity]}22`,
                      color: SEV_COLOR[a.severity],
                      border: `1px solid ${SEV_COLOR[a.severity]}55`,
                    }}
                  >
                    {a.severity.toUpperCase()}
                  </span>
                  {a.plant_name && <span>📍 {a.plant_name}</span>}
                  {a.metric_value != null && (
                    <span>
                      Current: <strong style={{ color: 'var(--text-primary)' }}>{a.metric_value}</strong>
                      {a.threshold != null && <> · Threshold: <strong style={{ color: 'var(--text-primary)' }}>{a.threshold}</strong></>}
                    </span>
                  )}
                  <span style={{ marginLeft: 'auto', color: 'var(--text-muted)' }}>
                    {new Date(a.timestamp).toLocaleTimeString('en-IN')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
