import { useState, useEffect, useCallback } from 'react'

/**
 * Generic data-fetching hook.
 * @param {Function} fetchFn  - API function that returns a Promise
 * @param {Object}   params   - Query params (re-fetches when these change)
 * @param {boolean}  immediate - Fetch immediately on mount (default: true)
 */
export function useApi(fetchFn, params = {}, immediate = true) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error,   setError]   = useState(null)

  const key = JSON.stringify(params)

  const fetch = useCallback(async (overrideParams) => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn(overrideParams ?? params)
      setData(result)
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  useEffect(() => {
    if (immediate) fetch()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  return { data, loading, error, refetch: fetch }
}
