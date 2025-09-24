import axios from 'axios'

const API_BASE_URL = ''  // Use relative path for CloudFront routing

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.dispatchEvent(new Event('auth-changed'))
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData)
}

export const attractionsAPI = {
  getAll: (params) => api.get('/api/attractions', { params }),
  getById: (id) => api.get(`/api/attractions/${id}`)
}

export const itineraryAPI = {
  create: (data) => api.post('/api/itineraries', data),
  getMine: () => api.get('/api/itineraries/me'),
  getByUser: (userId) => api.get(`/api/itineraries/user/${userId}`),
  remove: (itineraryId) => api.delete(`/api/itineraries/${itineraryId}`),
  clear: () => api.delete('/api/itineraries'),
  plan: (payload) => api.post('/api/itineraries/plan', payload)
}

export default api
