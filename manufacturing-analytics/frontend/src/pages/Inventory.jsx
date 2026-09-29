import { useApi } from '../hooks/useApi'
import { fetchInventoryStatus, fetchInventoryTrend } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge } from '../components/UI'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

export default function Inventory() {
  const { data: status, loading: sL, error: sE } = useApi(fetchInventoryStatus)
  const { data: trend,  loading: tL }             = useApi(fetchInventoryTrend, { granularity: 'monthly' })

  // Split items by stock status
  const lowStock   = (status || []).filter(i => i.stock_status !== 'OK')
  const allItems   = status || []

  return (
    <>
      <div className="section-title">Inventory Management</div>
      <div className="section-sub">Real-time stock levels, reorder alerts, and movement trends</div>

      {/* Summary KPIs */}
      <div className="kpi-grid" style={{ marginBottom: 20 }}>
        {[
          { label: 'Total Products',   value: allItems.length,                         icon: '📦', color: 'blue'   },
          { label: 'Out of Stock',     value: allItems.filter(i => i.stock_status === 'Out of Stock').length, icon: '🚫', color: 'red'    },
          { label: 'Low Stock',        value: allItems.filter(i => i.stock_status === 'Low Stock').length,   icon: '⚠️', color: 'yellow' },
          { label: 'Healthy Stock',    value: allItems.filter(i => i.stock_status === 'OK').length,          icon: '✅', color: 'green'  },
          { label: 'Total Stock Value',value: allItems.reduce((s,i) => s + (i.stock_value || 0), 0).toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }), icon: '💰', color: 'cyan' },
        ].map(k => (
          <div className={`kpi-card ${k.color}`} key={k.label}>
            <div className="kpi-icon">{k.icon}</div>
            <div className="kpi-value" style={{ fontSize: typeof k.value === 'string' && k.value.length > 8 ? 18 : 28 }}>{k.value}</div>
            <div className="kpi-label">{k.label}</div>
          </div>
        ))}
      </div>

      {/* Trend chart */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><div className="card-title">Monthly Inventory Movement</div></div>
        {tL ? <LoadingState /> : (
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trend || []} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
              <defs>
                <linearGradient id="gradIn"  x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gradOut" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="period" tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => v?.slice(0,7)} />
              <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => (v/1000).toFixed(0)+'K'} />
              <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} labelStyle={{ color: '#e6edf3' }} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#8b949e' }} />
              <Area type="monotone" dataKey="total_in"  name="Stock In"  stroke="#22c55e" fill="url(#gradIn)"  strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="total_out" name="Stock Out" stroke="#ef4444" fill="url(#gradOut)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Stock status table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Product Stock Status</div>
          <div className="card-subtitle">{lowStock.length} items need attention</div>
        </div>
        {sL ? <LoadingState /> : sE ? <ErrorState message={sE} /> : !allItems.length ? <EmptyState /> : (
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product</th><th>Code</th><th>Category</th>
                  <th>Current Stock</th><th>Reorder Level</th><th>Reorder Qty</th>
                  <th>Stock Value</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {allItems.map(i => (
                  <tr key={i.product_id}>
                    <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>{i.product_name}</td>
                    <td><code style={{ color: 'var(--accent-light)', fontSize: 11 }}>{i.product_code}</code></td>
                    <td>{i.category}</td>
                    <td>
                      <span className={i.current_stock === 0 ? 'text-danger fw-700' : i.is_below_reorder ? 'text-warning fw-700' : 'text-success'}>
                        {i.current_stock?.toLocaleString()}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{i.reorder_level?.toLocaleString()}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{i.reorder_quantity?.toLocaleString()}</td>
                    <td>₹{(i.stock_value || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                    <td><Badge status={i.stock_status} /></td>
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
