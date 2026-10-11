import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 60000,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const guestToken = sessionStorage.getItem('guest_token')
  if (guestToken) config.headers['X-Guest-Token'] = guestToken
  return config
})

// Handle 401 - clear tokens and redirect
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data: { email: string; password: string; name: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  logout: () => { localStorage.removeItem('access_token'); localStorage.removeItem('user') },
}

export const uploadAPI = {
  upload: (file: File, onProgress?: (pct: number) => void) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/uploads', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })
  },
  getSheets: (fileId: string) => api.get(`/uploads/${fileId}/sheets`),
  getPreview: (fileId: string, sheetName: string, page = 1, pageSize = 20) =>
    api.get(`/uploads/${fileId}/preview`, { params: { sheet_name: sheetName, page, page_size: pageSize } }),
  deleteUpload: (fileId: string) => api.delete(`/uploads/${fileId}`),
}

export const analysisAPI = {
  runAnalysis: (fileId: string, data: { sheet_name: string; name: string }) =>
    api.post(`/analysis/${fileId}/run`, data),
  getStatus: (reportId: string) => api.get(`/analysis/${reportId}/status`),
}

export const reportsAPI = {
  list: () => api.get('/reports'),
  get: (reportId: string) => api.get(`/reports/${reportId}`),
  getInsights: (reportId: string) => api.get(`/reports/${reportId}/insights`),
  getCharts: (reportId: string) => api.get(`/reports/${reportId}/charts`),
  rename: (reportId: string, name: string) => api.patch(`/reports/${reportId}`, { name }),
  delete: (reportId: string) => api.delete(`/reports/${reportId}`),
  exportPdf: (reportId: string) => api.get(`/reports/${reportId}/export/pdf`, { responseType: 'blob' }),
  exportCsv: (reportId: string, tableName: string) =>
    api.get(`/reports/${reportId}/export/csv`, { params: { table_name: tableName }, responseType: 'blob' }),
}

export const chatAPI = {
  send: (reportId: string, message: string) =>
    api.post(`/reports/${reportId}/chat`, { message }),
  history: (reportId: string) => api.get(`/reports/${reportId}/chat/history`),
  suggestions: (reportId: string) => api.get(`/reports/${reportId}/chat/suggestions`),
}

export const billingAPI = {
  plans: () => api.get('/billing/plans'),
  checkout: (planName: string) => api.post('/billing/checkout', { plan_name: planName }),
  verify: (data: { payment_id: string; order_id: string; signature: string }) =>
    api.post('/billing/verify', data),
  subscription: () => api.get('/subscriptions/me'),
}

export const healthAPI = {
  check: () => api.get('/health'),
}

export default api
