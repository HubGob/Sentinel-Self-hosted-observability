import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export default function Services() {
  const { data, isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: api.getServices,
  })

  if (isLoading) return <div className="text-center py-8">Loading...</div>

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Services</h2>
      <div className="bg-white shadow overflow-hidden rounded-md">
        <ul className="divide-y divide-gray-200">
          {data?.services.map((service) => (
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
