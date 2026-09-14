import { useQuery } from '@tanstack/react-query'
import { Area, AreaChart, ResponsiveContainer, Tooltip } from 'recharts'
import { api, ServiceStatus } from '../api/client'

// The API emits naive UTC timestamps; append Z so the browser doesn't read them as local.
function parseTimestamp(value: string): Date {
  return new Date(value.endsWith('Z') ? value : `${value}Z`)
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return 'ongoing'
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  return `${(seconds / 3600).toFixed(1)}h`
}

function dotClass(status: string): string {
  if (status === 'up') return 'bg-emerald-500'
  if (status === 'down') return 'bg-red-500'
  return 'bg-gray-400'
}

function Sparkline({ service }: { service: ServiceStatus }) {
  const gradientId = `spark-${service.service.replace(/[^a-zA-Z0-9]/g, '-')}`
  const hasFailure = service.recent.some((point) => point.status === 'down')
  const stroke = hasFailure ? '#ef4444' : '#10b981'
  const data = service.recent.map((point, index) => ({
    index,
    latency: point.latency_ms ?? 0,
  }))

  if (data.length < 2) {
    return (
      <div className="h-14 flex items-center text-xs text-gray-400">
        Not enough data for a trend yet.
      </div>
    )
  }

  return (
    <div className="h-14 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={stroke} stopOpacity={0.35} />
              <stop offset="100%" stopColor={stroke} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Tooltip formatter={(value) => [`${value} ms`, 'Latency']} labelFormatter={() => ''} />
          <Area
            type="monotone"
            dataKey="latency"
            stroke={stroke}
            strokeWidth={2}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

function UptimeStat({ label, value }: { label: string; value: number }) {
  const tone = value >= 99 ? 'text-emerald-600' : value >= 95 ? 'text-amber-600' : 'text-red-600'
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className={`text-lg font-semibold ${tone}`}>{value.toFixed(2)}%</div>
    </div>
  )
}

export default function Status() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['status'],
    queryFn: api.getStatus,
    refetchInterval: 5000,
  })
  const { data: incidentData } = useQuery({
    queryKey: ['incidents'],
    queryFn: api.getIncidents,
    refetchInterval: 30000,
  })

  const services = data?.services ?? []
  const incidents = incidentData?.incidents ?? []
  const downCount = services.filter((service) => service.status === 'down').length
  const allUp = services.length > 0 && downCount === 0
  const headline =
    services.length === 0
      ? 'No services are being monitored yet.'
      : allUp
        ? 'All systems operational'
        : `${downCount} service${downCount === 1 ? '' : 's'} down`

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <h1 className="text-3xl font-bold text-gray-900">Sentinel Status</h1>
          <div className="mt-3 flex items-center gap-3">
            <span
              className={`inline-block h-3 w-3 rounded-full ${
                allUp ? 'bg-emerald-500' : downCount > 0 ? 'bg-red-500' : 'bg-gray-400'
              }`}
            />
            <p className="text-gray-600">{headline}</p>
          </div>
          <p className="mt-1 text-xs text-gray-400">Refreshes every 5 seconds.</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-4">
        {isLoading && <p className="text-gray-500">Loading…</p>}
        {isError && (
          <p className="text-red-600">Could not reach the collector API.</p>
        )}

        {services.map((service) => (
          <section
            key={service.service}
            className="bg-white rounded-lg border shadow-sm p-5"
            data-testid="service-card"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <span className={`inline-block h-3 w-3 rounded-full ${dotClass(service.status)}`} />
                <div>
                  <h2 className="font-semibold text-gray-900">{service.service}</h2>
                  {service.url && (
                    <a
                      href={service.url}
                      className="text-sm text-indigo-600 hover:text-indigo-800 break-all"
                      target="_blank"
                      rel="noreferrer"
                    >
                      {service.url}
                    </a>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs uppercase tracking-wide text-gray-500">Latency</div>
                <div className="text-lg font-semibold text-gray-900">
                  {service.latency_ms === null ? '—' : `${service.latency_ms} ms`}
                </div>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-3 gap-4">
              <UptimeStat label="Last 24h" value={service.uptime_24h} />
              <UptimeStat label="Last 7d" value={service.uptime_7d} />
              <UptimeStat label="Last 30d" value={service.uptime_30d} />
            </div>

            <div className="mt-4">
              <Sparkline service={service} />
            </div>
          </section>
        ))}

        <section className="bg-white rounded-lg border shadow-sm p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Recent incidents</h2>
          {incidents.length === 0 ? (
            <p className="text-sm text-gray-500">No incidents recorded.</p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {incidents.map((incident) => (
                <li key={incident.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{incident.service}</p>
                    <p className="text-sm text-gray-500">
                      {parseTimestamp(incident.opened_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-700">
                      {formatDuration(incident.duration_sec)}
                    </p>
                    <p
                      className={`text-xs ${
                        incident.closed_at ? 'text-emerald-600' : 'text-red-600'
                      }`}
                    >
                      {incident.closed_at ? 'resolved' : 'ongoing'}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  )
}
