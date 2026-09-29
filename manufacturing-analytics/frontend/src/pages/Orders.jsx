import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchOrders } from '../services/api'
import { LoadingState, ErrorState, EmptyState, Badge, Pagination } from '../components/UI'

export default function Orders() {
  const [page,   setPage]   = useState(1)
  const [filter, setFilter] = useState({ status: '', priority: '', customer: '' })

  const params = {
    page, page_size: 50,
    ...Object.fromEntries(Object.entries(filter).filter(([, v]) => v !== '')),
  }

  const { data, loading, error } = useApi(fetchOrders, params)
  const totalPages = data ? Math.ceil(data.total / 50) : 1

  // Status summary from current page
  const statusCounts = (data?.data || []).reduce((acc, o) => {
    acc[o.status] = (acc[o.status] || 0) + 1; return acc
  }, {})

  return (
    <>
      <div className="section-title">Orders</div>
      <div className="section-sub">Customer order tracking and delivery status</div>

      {/* Filter bar */}
      <div className="filters-bar">
        <input className="filter-input" placeholder="Search customer…" value={filter.customer}
          onChange={e => { setFilter(f => ({ ...f, customer: e.target.value })); setPage(1) }}
          style={{ minWidth: 200 }}
        />
        <select className="filter-select" value={filter.status}
          onChange={e => { setFilter(f => ({ ...f, status: e.target.value })); setPage(1) }}>
          <option value="">All Statuses</option>
          {['Pending','Confirmed','In Production','Completed','Shipped','Cancelled'].map(s => <option key={s}>{s}</option>)}
        </select>
        <select className="filter-select" value={filter.priority}
          onChange={e => { setFilter(f => ({ ...f, priority: e.target.value })); setPage(1) }}>
          <option value="">All Priorities</option>
          {['Low','Normal','High','Urgent'].map(p => <option key={p}>{p}</option>)}
        </select>
        <span className="text-muted" style={{ fontSize: 12 }}>
          {data ? `${data.total.toLocaleString()} orders` : ''}
        </span>
      </div>

      <div className="card">
        {loading ? <LoadingState /> : error ? <ErrorState message={error} /> : !data?.data?.length ? <EmptyState /> : (
          <>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Order #</th><th>Customer</th><th>Product</th>
                    <th>Qty</th><th>Amount</th><th>Order Date</th>
                    <th>Expected</th><th>Priority</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.map(o => {
                    const late = o.status !== 'Completed' && o.status !== 'Shipped' && o.status !== 'Cancelled'
                      && new Date(o.expected_delivery) < new Date()
                    return (
                      <tr key={o.order_id}>
                        <td><code style={{ color: 'var(--accent-light)', fontSize: 11 }}>{o.order_number}</code></td>
                        <td style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis' }}>{o.customer_name}</td>
                        <td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{o.product_name}</td>
                        <td>{o.quantity_ordered?.toLocaleString()}</td>
                        <td>₹{Number(o.total_amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                        <td>{o.order_date}</td>
                        <td className={late ? 'text-danger fw-700' : ''}>{o.expected_delivery}</td>
                        <td><Badge status={o.priority} /></td>
                        <td><Badge status={o.status} /></td>
                      </tr>
                    )
                  })}
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
