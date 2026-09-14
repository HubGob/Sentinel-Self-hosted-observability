import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import EmptyState from '../components/EmptyState'

export default function Services() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['services'],
    queryFn: api.getServices,
  })

  const services = data?.services ?? []

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Services</h2>
      <div className="bg-white shadow overflow-hidden rounded-md">
        {isLoading && <EmptyState title="Loading services…" />}
        {isError && (
          <EmptyState title="Could not load services." hint="Check that the API is reachable." />
        )}
        {!isLoading && !isError && services.length === 0 && (
          <EmptyState
            title="No services yet."
            hint={
              <>
                Run the agent, or POST to <code className="font-mono">/api/v1/ingest</code>, to
                start collecting.
              </>
            }
          />
        )}
        <ul className="divide-y divide-gray-200">
          {services.map((service) => (
            <li key={service.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div>
                  <Link
                    to={`/logs?service_id=${service.id}`}
                    className="text-indigo-600 hover:text-indigo-900 font-medium"
                  >
                    {service.name}
                  </Link>
                  <p className="text-sm text-gray-500">
                    Last seen: {service.last_seen_at || 'Never'}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
