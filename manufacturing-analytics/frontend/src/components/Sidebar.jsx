import { NavLink, useLocation } from 'react-router-dom'

const NAV = [
  { to: '/',            icon: '📊', label: 'Dashboard' },
  { to: '/production',  icon: '🏭', label: 'Production' },
  { to: '/machines',    icon: '⚙️',  label: 'Machines' },
  { to: '/quality',     icon: '🔬', label: 'Quality' },
  { to: '/inventory',   icon: '📦', label: 'Inventory' },
  { to: '/maintenance', icon: '🔧', label: 'Maintenance' },
  { to: '/orders',      icon: '📋', label: 'Orders' },
  { to: '/alerts',      icon: '🚨', label: 'Alerts' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🏗️</div>
        <h2>MFG Intelligence</h2>
        <p>Operations Analytics</p>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {NAV.map(n => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{n.icon}</span>
            {n.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        Manufacturing Analytics v1.0<br />
        Data: 2023–2024
      </div>
    </aside>
  )
}
