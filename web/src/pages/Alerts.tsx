import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export default function Alerts() {
  const { data, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(),
  })

  if (isLoading) return <div className="text-center py-8">Loading...</div>

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Alerts</h2>
      <div className="bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {data?.alerts.map((alert) => (
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
