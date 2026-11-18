/**
 * RoadSense – Axios API instance
 * All requests go through this configured client with automatic JWT token attachment.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor – attach JWT token & normalize double /api prefixes ─
api.interceptors.request.use((config) => {
  // Fix double /api prefix
  if (config.url && config.url.startsWith('/api/') && config.baseURL === '/api') {
    config.url = config.url.replace(/^\/api/, '')
  }

  // Attach JWT Bearer token if present
  const token = localStorage.getItem('roadsense_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// ── Response interceptor – normalise errors & handle 401 ─────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const normalised = {
      message: 'An unexpected error occurred.',
      status: null,
      detail: null,
    }

    if (error.response) {
      normalised.status = error.response.status
      const data = error.response.data

      // If token expired / unauthorized, clear stale token
      if (error.response.status === 401 && !error.config.url.includes('/auth/login')) {
        localStorage.removeItem('roadsense_token')
        localStorage.removeItem('roadsense_user')
      }

      if (typeof data === 'string') {
        normalised.message = data
      } else if (data?.detail) {
        normalised.message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail)
        normalised.detail = data.detail
      } else if (data?.message) {
        normalised.message = data.message
      } else {
        normalised.message = `Server error (${normalised.status})`
      }
    } else if (error.request) {
      normalised.message =
        'No response received from the server. Check your connection.'
    } else {
      normalised.message = error.message || 'Request configuration error.'
    }

    return Promise.reject(normalised)
  }
)

export default api
