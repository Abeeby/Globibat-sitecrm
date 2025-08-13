import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import config from '../config';

const api = axios.create({
  baseURL: config.API_URL,
  timeout: config.REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('@token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      await AsyncStorage.removeItem('@token');
      await AsyncStorage.removeItem('@user');
      // Redirection vers login sera gérée par AuthContext
    }
    return Promise.reject(error);
  }
);

// Services API
const apiService = {
  // Authentification
  auth: {
    login: (email, password) => api.post('/auth/login', { email, password }),
    logout: () => api.post('/auth/logout'),
    refresh: () => api.post('/auth/refresh'),
    profile: () => api.get('/auth/profile'),
  },

  // Employés
  employees: {
    getAll: (params) => api.get('/api/employes', { params }),
    getOne: (id) => api.get(`/api/employes/${id}`),
    create: (data) => api.post('/api/employes', data),
    update: (id, data) => api.put(`/api/employes/${id}`, data),
    delete: (id) => api.delete(`/api/employes/${id}`),
    getByMatricule: (matricule) => api.get(`/api/employes/matricule/${matricule}`),
  },

  // Badges avec matricule
  badges: {
    create: (data) => api.post('/api/badges', data),
    getToday: () => api.get('/api/badges/today'),
    getByEmployee: (employeeId) => api.get(`/api/badges/employee/${employeeId}`),
    getByMatricule: (matricule) => api.get(`/api/badges/matricule/${matricule}`),
    submitBadge: (matricule, type, location) => 
      api.post('/api/badges/submit', { 
        matricule, 
        type_badge: type,
        latitude: location?.latitude,
        longitude: location?.longitude,
        timestamp: new Date().toISOString()
      }),
    close: (id) => api.post(`/api/badges/${id}/close`),
    delete: (id) => api.delete(`/api/badges/${id}`),
    getAnomalies: () => api.get('/api/badges/anomalies'),
  },

  // Clients
  clients: {
    getAll: (params) => api.get('/api/clients', { params }),
    getOne: (id) => api.get(`/api/clients/${id}`),
    create: (data) => api.post('/api/clients', data),
    update: (id, data) => api.put(`/api/clients/${id}`, data),
    delete: (id) => api.delete(`/api/clients/${id}`),
    getProjects: (clientId) => api.get(`/api/clients/${clientId}/chantiers`),
  },

  // Chantiers
  projects: {
    getAll: (params) => api.get('/api/chantiers', { params }),
    getOne: (id) => api.get(`/api/chantiers/${id}`),
    create: (data) => api.post('/api/chantiers', data),
    update: (id, data) => api.put(`/api/chantiers/${id}`, data),
    delete: (id) => api.delete(`/api/chantiers/${id}`),
    getEmployees: (id) => api.get(`/api/chantiers/${id}/employes`),
  },

  // Factures
  invoices: {
    getAll: (params) => api.get('/api/factures', { params }),
    getOne: (id) => api.get(`/api/factures/${id}`),
    create: (data) => api.post('/api/factures', data),
    update: (id, data) => api.put(`/api/factures/${id}`, data),
    delete: (id) => api.delete(`/api/factures/${id}`),
    getPDF: (id) => api.get(`/api/factures/${id}/pdf`, { responseType: 'blob' }),
    markPaid: (id) => api.post(`/api/factures/${id}/paid`),
    sendEmail: (id) => api.post(`/api/factures/${id}/send`),
  },

  // Dashboard
  dashboard: {
    getStats: () => api.get('/api/stats'),
    getNotifications: () => api.get('/api/notifications'),
    getRecentActivity: () => api.get('/api/activity'),
  },

  // Notifications
  notifications: {
    register: (token) => api.post('/api/notifications/register', { token }),
    getAll: () => api.get('/api/notifications'),
    markRead: (id) => api.put(`/api/notifications/${id}/read`),
    markAllRead: () => api.put('/api/notifications/read-all'),
    delete: (id) => api.delete(`/api/notifications/${id}`),
  },

  // WebSocket test
  websocket: {
    test: (type, data) => api.post('/api/websocket/test', { type, ...data }),
    stats: () => api.get('/api/websocket/stats'),
  },
};

export default api;
export { apiService };