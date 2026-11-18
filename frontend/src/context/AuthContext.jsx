/**
 * RoadSense – Authentication Context & Hook
 * Manages JWT session state, login, registration, and logout.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../config/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('roadsense_token'))
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('roadsense_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  // Verify token on mount by calling /api/auth/me
  useEffect(() => {
    async function verifySession() {
      const savedToken = localStorage.getItem('roadsense_token')
      if (!savedToken) {
        setUser(null)
        setLoading(false)
        return
      }

      try {
        const res = await api.get('/api/auth/me')
        setUser(res.data)
        localStorage.setItem('roadsense_user', JSON.stringify(res.data))
      } catch (err) {
        console.warn('Session expired or invalid token:', err?.message)
        localStorage.removeItem('roadsense_token')
        localStorage.removeItem('roadsense_user')
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    verifySession()
  }, [])

  const login = useCallback(async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('roadsense_token', access_token)
    localStorage.setItem('roadsense_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return userData
  }, [])

  const register = useCallback(async (name, email, password, role = 'inspector') => {
    const res = await api.post('/api/auth/register', { name, email, password, role })
    const { access_token, user: userData } = res.data
    localStorage.setItem('roadsense_token', access_token)
    localStorage.setItem('roadsense_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return userData
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('roadsense_token')
    localStorage.removeItem('roadsense_user')
    setToken(null)
    setUser(null)
  }, [])

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    loading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
