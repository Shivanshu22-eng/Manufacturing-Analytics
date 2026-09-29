import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchKPIs, fetchProdTrend, fetchProdByPlant, fetchDefectSummary, fetchDowntime } from '../services/api'
import { KPICard, LoadingState, ErrorState } from '../components/UI'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const COLORS = ['#3b82f6','#22c55e','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#f97316','#ec4899']

const fmt = (v) => typeof v === 'number' ? v.toLocaleString('en-IN') : v

export default function Dashboard() {
  const [dateFrom, setDateFrom] = useState('2024-01-01')
  const [dateTo,   setDateTo]   = useState('2024-12-31')

  const { data: kpis,    loading: kL, error: kE }   = useApi(fetchKPIs)
  const { data: trend,   loading: tL }               = useApi(fetchProdTrend, { granularity: 'monthly' })
  const { data: byPlant, loading: pL }               = useApi(fetchProdByPlant)
  const { data: defSum,  loading: dL }               = useApi(fetchDefectSummary)
  const { data: downtime,loading: dtL }              = useApi(fetchDowntime, { top_n: 8 })

  if (kL) return <LoadingState />
  if (kE) return <ErrorState message={kE} />

  return (
    <>
      <div className="section-title">Operations Dashboard</div>
      <div className="section-sub">Real-time overview — Manufacturing Plants across India · 2023–2024</div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard icon="🏭" label="Production Runs"      value={kpis?.total_production_runs}  color="blue" />
        <KPICard icon="📦" label="Units Produced"        value={kpis?.total_units_produced}   color="green" />
        <KPICard icon="⚡" label="Avg Efficiency"        value={kpis?.avg_efficiency_pct}     unit="%" color="cyan" />
        <KPICard icon="🔬" label="Overall Defect Rate"   value={kpis?.overall_defect_rate_pct}unit="%" color="yellow" />
        <KPICard icon="⚙️"  label="Operational Machines" value={`${kpis?.operational_machines}/${kpis?.total_machines}`} color="purple" />
        <KPICard icon="⏱️" label="Total Downtime"        value={kpis?.total_downtime_hours}   unit="h" color="red" />
        <KPICard icon="⚠️" label="Low Stock Items"       value={kpis?.low_stock_products}     color="yellow" />
        <KPICard icon="📋" label="Active Orders"         value={kpis?.active_orders}          color="blue" />
        <KPICard icon="💰" label="Total Revenue"         value={kpis?.revenue ? `₹${(kpis.revenue/1e7).toFixed(1)}Cr` : '—'} color="green" />
      </div>

      {/* Production Trend + By Plant */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Monthly Production Trend</div>
              <div className="card-subtitle">Planned vs Actual output</div>
            </div>
          </div>
          {tL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={trend || []} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
                <defs>
                  <linearGradient id="gradPlanned" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="period" tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => v?.slice(0,7)} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => (v/1000).toFixed(0)+'K'} />
                <Tooltip
                  contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
                  labelStyle={{ color: '#e6edf3' }}
                  formatter={(v, n) => [fmt(v), n === 'total_planned' ? 'Planned' : 'Actual']}
                />
                <Area type="monotone" dataKey="total_planned" fill="url(#gradPlanned)" stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Area type="monotone" dataKey="total_actual"  fill="url(#gradActual)"  stroke="#22c55e" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Production by Plant</div>
          </div>
          {pL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={byPlant || []} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} tickFormatter={v => (v/1000).toFixed(0)+'K'} />
                <YAxis type="category" dataKey="plant_name" tick={{ fill: '#8b949e', fontSize: 10 }} width={110} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} labelStyle={{ color: '#e6edf3' }} />
                <Bar dataKey="total_actual" name="Units Produced" radius={[0, 4, 4, 0]}>
                  {(byPlant || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Defect Summary + Machine Downtime */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <div className="card-title">Top Machines by Downtime</div>
          </div>
          {dtL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={downtime || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#8b949e', fontSize: 11 }} />
                <YAxis type="category" dataKey="machine_name" tick={{ fill: '#8b949e', fontSize: 10 }} width={130} />
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} labelStyle={{ color: '#e6edf3' }} />
                <Bar dataKey="downtime_hours" name="Downtime (hrs)" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Defects by Category</div>
          </div>
          {dL ? <LoadingState /> : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={defSum || []} dataKey="count"
                  nameKey="defect_category"
                  cx="50%" cy="50%" outerRadius={90}
                  label={({ name, pct_of_total }) => `${pct_of_total}%`}
                  labelLine={false}
                >
                  {(defSum || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: '#8b949e' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </>
  )
}
