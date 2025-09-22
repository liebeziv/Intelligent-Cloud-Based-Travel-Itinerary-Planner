import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://travelplannerbackend-env.eba-p7nfszip.us-east-1.elasticbeanstalk.com',
  timeout: 10000
})

// Request interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
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
  getByUser: (userId) => api.get(`/api/itineraries/user/${userId}`)
}

export default api
