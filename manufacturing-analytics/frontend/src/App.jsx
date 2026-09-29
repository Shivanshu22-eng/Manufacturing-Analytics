import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard  from './pages/Dashboard'
import Production from './pages/Production'
import Machines   from './pages/Machines'
import Quality    from './pages/Quality'
import Inventory  from './pages/Inventory'
import Maintenance from './pages/Maintenance'
import Orders     from './pages/Orders'
import Alerts     from './pages/Alerts'

const PAGE_TITLES = {
  '/':            { title: 'Dashboard',   sub: 'Executive overview of all operations' },
  '/production':  { title: 'Production',  sub: 'Production run history and efficiency' },
  '/machines':    { title: 'Machines',    sub: 'Fleet utilization and downtime tracking' },
  '/quality':     { title: 'Quality Control', sub: 'Defect analytics and inspection records' },
  '/inventory':   { title: 'Inventory',   sub: 'Stock levels and movement trends' },
  '/maintenance': { title: 'Maintenance', sub: 'Scheduled and overdue maintenance tasks' },
  '/orders':      { title: 'Orders',      sub: 'Customer order tracking and delivery status' },
  '/alerts':      { title: 'Alerts',      sub: 'Live operational alerts and notifications' },
}

function Topbar() {
  const path = window.location.pathname
  const info = PAGE_TITLES[path] || PAGE_TITLES['/']
  return (
    <header className="topbar">
      <div className="topbar-title">
        <h1>{info.title}</h1>
        <p>{info.sub}</p>
      </div>
      <div className="topbar-right">
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          {new Date().toLocaleDateString('en-IN', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })}
        </span>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: 'var(--success)', boxShadow: '0 0 8px var(--success)',
        }} title="API Connected" />
      </div>
    </header>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div className="main-content">
          <Topbar />
          <main className="page-content">
            <Routes>
              <Route path="/"            element={<Dashboard />} />
              <Route path="/production"  element={<Production />} />
              <Route path="/machines"    element={<Machines />} />
              <Route path="/quality"     element={<Quality />} />
              <Route path="/inventory"   element={<Inventory />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/orders"      element={<Orders />} />
              <Route path="/alerts"      element={<Alerts />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
