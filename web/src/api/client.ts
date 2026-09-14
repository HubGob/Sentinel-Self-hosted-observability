const API_BASE = import.meta.env.VITE_API_URL || ''
const TOKEN_KEY = 'sentinel.tokens'

export interface Tokens {
  access_token: string
  refresh_token: string
  token_type: string
}

function readStoredTokens(): Tokens | null {
  try {
    const raw = localStorage.getItem(TOKEN_KEY)
    return raw ? (JSON.parse(raw) as Tokens) : null
  } catch {
    // A malformed entry should log the user out, not crash the app on boot.
    return null
  }
}

let tokens: Tokens | null = readStoredTokens()
let refreshInFlight: Promise<Tokens | null> | null = null

export function getTokens(): Tokens | null {
  return tokens
}

export function setTokens(next: Tokens | null): void {
  tokens = next
  if (next) {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(next))
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

async function refreshTokens(): Promise<Tokens | null> {
  const current = tokens
  if (!current) return null

  // Collapse concurrent refreshes. Ten queries failing at once should produce
  // one refresh call, not ten racing ones.
  refreshInFlight ??= (async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: current.refresh_token }),
      })
      if (!response.ok) return null
      const next = (await response.json()) as Tokens
      setTokens(next)
      return next
    } catch {
      return null
    } finally {
      refreshInFlight = null
    }
  })()

  return refreshInFlight
}

async function fetchJSON<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers)
  if (tokens) headers.set('Authorization', `Bearer ${tokens.access_token}`)

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (response.status === 401 && retry && tokens) {
    // The access token is short-lived by design, so a 401 usually just means
    // it expired. Refresh once and replay the request before giving up.
    const refreshed = await refreshTokens()
    if (refreshed) return fetchJSON<T>(path, options, false)
    setTokens(null)
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json() as Promise<T>
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
    return fetchJSON<{ logs: Log[]; total: number; limit: number; offset: number }>(
      `/api/v1/logs?${query}`,
    )
  },
  getAlerts: (params?: { limit?: number; offset?: number }) => {
    const query = new URLSearchParams()
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.offset) query.set('offset', String(params.offset))
    return fetchJSON<{ alerts: Alert[]; total: number; limit: number; offset: number }>(
      `/api/v1/alerts?${query}`,
    )
  },
  getStatus: () => fetchJSON<{ services: ServiceStatus[] }>('/api/v1/status'),
  getIncidents: () => fetchJSON<{ incidents: Incident[] }>('/api/v1/incidents'),
}

export const auth = {
  /** Register and store the returned tokens. */
  async register(email: string, password: string): Promise<Tokens> {
    const next = await fetchJSON<Tokens>(
      '/api/v1/auth/register',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      },
      false,
    )
    setTokens(next)
    return next
  },

  /** Log in and store the returned tokens. */
  async login(email: string, password: string): Promise<Tokens> {
    const next = await fetchJSON<Tokens>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      },
      false,
    )
    setTokens(next)
    return next
  },

  logout(): void {
    setTokens(null)
  },

  isAuthenticated(): boolean {
    return tokens !== null
  },
}
