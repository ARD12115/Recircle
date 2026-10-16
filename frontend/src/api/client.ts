import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/ui'
import { ScanConfirmationResponse, ScanResult, TwinResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Request interceptor - attach token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken } = useAuthStore.getState()
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// Response interceptor - handle 401, extract request_id
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const { refreshToken, logout, setAccessToken } = useAuthStore.getState()
    
    if (error.response?.status === 401 && refreshToken) {
      try {
        const res = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {}, {
          headers: {},
        })
        setAccessToken(res.data.access_token)
        // Retry original request
        error.config!.headers.Authorization = `Bearer ${res.data.access_token}`
        return api.request(error.config!)
      } catch {
        logout()
        window.location.href = '/login'
      }
    }
    
    // Attach request_id to error for debugging
    const requestId = error.response?.headers['x-request-id']
    if (requestId) {
      (error as any).requestId = requestId
    }
    
    return Promise.reject(error)
  }
)

export const scanApi = {
  scan: (file: File, sourceNodeId?: number) => {
    const form = new FormData()
    form.append('file', file)
    if (sourceNodeId !== undefined) form.append('source_node_id', String(sourceNodeId))
    return api.post<ScanResult>('/scan', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  confirm: (scanId: string, confirmedBin: string) =>
    api.post<ScanConfirmationResponse>(`/scan/${scanId}/confirm`, { confirmed_bin: confirmedBin }),
  history: (page = 1, pageSize = 20) => api.get('/scans', { params: { page, page_size: pageSize } }),
}

export const twinApi = {
  get: () => api.get<TwinResponse>('/twin'),
  stream: () => `${API_BASE}/api/v1/twin/stream`,
  simulate: (params: import('../types').SimulateParams) =>
    api.post<import('../types').SimulateResponse>('/simulate', params),
}

export const adviceApi = {
  get: (useCached = false) => api.post('/advice', null, { params: { use_cached: useCached } }),
  chat: (messages: any[]) => api.post('/chat', { messages }),
}

export const authApi = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  refresh: (refreshToken: string) => api.post('/auth/refresh', {}, { headers: {} }),
  demo: (role: string) => api.post(`/auth/demo/${role}`),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
}

export const reportApi = {
  generate: () => api.post('/reports', {}, { responseType: 'blob' }),
}

export const adminApi = {
  resetDemo: () => api.post('/admin/demo/reset'),
  traffic: (start: boolean) => api.post('/admin/demo/traffic', null, { params: { start } }),
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
    public requestId?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
  
  static fromAxios(error: AxiosError): ApiError {
    const data = error.response?.data as any
    return new ApiError(
      data?.message || error.message,
      error.response?.status || 0,
      data?.code || 'UNKNOWN',
      (error as any).requestId
    )
  }
}