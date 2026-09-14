const API_BASE = import.meta.env.VITE_API_URL || ''

async function fetchJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export interface Service {
  id: string
  name: string
  created_at: string
  last_seen_at: string | null
}

export interface Log {
  id: string
  service_id: string
  timestamp: string
  level: string
  message: string
  source: string | null
  container_id: string | null
  container_name: string | null
}

export interface Alert {
  id: string
  rule_id: string
  service_id: string
  triggered_at: string
  resolved_at: string | null
  value: number
  message: string
}

export interface CheckPoint {
  checked_at: string
  status: string
  latency_ms: number | null
}

export interface ServiceStatus {
  service: string
  url: string | null
  status: string
  latency_ms: number | null
  uptime_24h: number
  uptime_7d: number
  uptime_30d: number
  last_checked_at: string | null
  recent: CheckPoint[]
}

export interface Incident {
  id: string
  service: string
  opened_at: string
  closed_at: string | null
  duration_sec: number | null
}

export const api = {
  getServices: () => fetchJSON<{ services: Service[]; total: number }>('/api/v1/services'),
  getLogs: (params?: { limit?: number; offset?: number; service_id?: string; level?: string }) => {
    const query = new URLSearchParams()
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.offset) query.set('offset', String(params.offset))
    if (params?.service_id) query.set('service_id', params.service_id)
    if (params?.level) query.set('level', params.level)
    return fetchJSON<{ logs: Log[]; total: number; limit: number; offset: number }>(`/api/v1/logs?${query}`)
  },
  getAlerts: (params?: { limit?: number; offset?: number }) => {
    const query = new URLSearchParams()
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.offset) query.set('offset', String(params.offset))
    return fetchJSON<{ alerts: Alert[]; total: number; limit: number; offset: number }>(`/api/v1/alerts?${query}`)
  },
  getStatus: () => fetchJSON<{ services: ServiceStatus[] }>('/api/v1/status'),
  getIncidents: () => fetchJSON<{ incidents: Incident[] }>('/api/v1/incidents'),
}
