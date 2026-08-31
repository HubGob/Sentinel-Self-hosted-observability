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
}
