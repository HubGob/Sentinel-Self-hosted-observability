import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: 'bg-gray-100 text-gray-800',
  INFO: 'bg-blue-100 text-blue-800',
  WARNING: 'bg-yellow-100 text-yellow-800',
  ERROR: 'bg-red-100 text-red-800',
  CRITICAL: 'bg-red-200 text-red-900',
}

export default function Logs() {
  const [searchParams] = useSearchParams()
  const serviceId = searchParams.get('service_id') || undefined
  const level = searchParams.get('level') || undefined

  const { data, isLoading } = useQuery({
    queryKey: ['logs', serviceId, level],
    queryFn: () => api.getLogs({ service_id: serviceId, level }),
  })

  if (isLoading) return <div className="text-center py-8">Loading...</div>

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Logs</h2>
      <div className="bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {data?.logs.map((log) => (
            <li key={log.id} className="px-6 py-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${LEVEL_COLORS[log.level] || ''}`}>
                      {log.level}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                    {log.container_name && (
                      <span className="text-xs text-gray-400">{log.container_name}</span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{log.message}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
