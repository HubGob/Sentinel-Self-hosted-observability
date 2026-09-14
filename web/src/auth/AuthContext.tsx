import { ReactNode, createContext, useCallback, useContext, useState } from 'react'
import { auth } from '../api/client'

interface AuthValue {
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(auth.isAuthenticated())

  const login = useCallback(async (email: string, password: string) => {
    await auth.login(email, password)
    setIsAuthenticated(true)
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    await auth.register(email, password)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(() => {
    auth.logout()
    setIsAuthenticated(false)
  }, [])

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside an AuthProvider')
  return value
}
