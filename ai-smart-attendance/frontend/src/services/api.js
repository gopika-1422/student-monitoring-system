import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use((config) => {
  const stored = JSON.parse(localStorage.getItem('auth-storage') || '{}')
  const token = stored?.state?.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API helpers
export const analyticsApi = {
  overview: () => api.get('/api/analytics/overview'),
  dailyTrend: (days = 30) => api.get(`/api/analytics/daily-trend?days=${days}`),
  emotionTrend: (days = 7) => api.get(`/api/analytics/emotion-trend?days=${days}`),
  alerts: (unreadOnly = false) => api.get(`/api/analytics/alerts?unread_only=${unreadOnly}`),
  markAlertRead: (id) => api.patch(`/api/analytics/alerts/${id}/read`),
  exportCsv: (params) => api.get('/api/analytics/export/csv', { params, responseType: 'blob' }),
}

export const studentsApi = {
  list: (params) => api.get('/api/students/', { params }),
  count: () => api.get('/api/students/count'),
  create: (data) => api.post('/api/students/', data),
  get: (id) => api.get(`/api/students/${id}`),
  update: (id, data) => api.put(`/api/students/${id}`, data),
  delete: (id) => api.delete(`/api/students/${id}`),
  uploadPhoto: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/api/students/${id}/photo`, form)
  },
  classes: () => api.get('/api/students/classes/list'),
  attendanceHistory: (id, days = 30) => api.get(`/api/attendance/by-student/${id}?days=${days}`),
}

export const attendanceApi = {
  list: (params) => api.get('/api/attendance/', { params }),
  stats: (classN) => api.get('/api/attendance/stats', { params: { class_name: classN } }),
  topStudents: (limit = 10) => api.get(`/api/attendance/top-students?limit=${limit}`),
  lowAttendance: (threshold = 75) => api.get(`/api/attendance/low-attendance-alerts?threshold=${threshold}`),
}

export const chatApi = {
  send: (message, history = []) => api.post('/api/chat/', { message, history }),
  health: () => api.get('/api/chat/health'),
}

export default api
