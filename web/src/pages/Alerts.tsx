import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import EmptyState from '../components/EmptyState'

export default function Alerts() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(),
  })

  const alerts = data?.alerts ?? []

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Alerts</h2>
      <div className="bg-white shadow overflow-hidden rounded-md">
        {isLoading && <EmptyState title="Loading alerts…" />}
        {isError && (
          <EmptyState title="Could not load alerts." hint="Check that the API is reachable." />
        )}
        {!isLoading && !isError && alerts.length === 0 && (
          <EmptyState
            title="No alerts have fired."
            hint="Alerts appear here when a rule matches incoming logs."
          />
        )}
        <ul className="divide-y divide-gray-200">
          {alerts.map((alert) => (
            <li key={alert.id} className="px-6 py-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                  <p className="text-sm text-gray-500">
                    Triggered: {new Date(alert.triggered_at).toLocaleString()}
                  </p>
                </div>
                {!alert.resolved_at && (
                  <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                    Active
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
