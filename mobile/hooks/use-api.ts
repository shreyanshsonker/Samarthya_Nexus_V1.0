import axios from 'axios';
import { useAuthStore } from './use-stores';

const API_BASE_URL = 'http://localhost:8000'; // Default dev URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const api = {
  auth: {
    login: (credentials: any) => apiClient.post('/auth/login', credentials),
    register: (userData: any) => apiClient.post('/auth/register', userData),
    verify: () => apiClient.get('/auth/verify'),
  },
  energy: {
    getCurrent: () => apiClient.get('/api/energy/current'),
    getHistory: (days = 7) => apiClient.get(`/api/energy/history?days=${days}`),
  },
  carbon: {
    getLive: () => apiClient.get('/api/carbon/live'),
    getDailySummary: () => apiClient.get('/api/carbon/daily-summary'),
    getWeeklySummary: () => apiClient.get('/api/carbon/weekly-summary'),
  },
  forecast: {
    getSolar: () => apiClient.get('/api/forecast/current'),
    getGreenWindow: () => apiClient.get('/api/forecast/green-window'),
    getExplanations: () => apiClient.get('/api/forecast/explain'),
  },
  recommendations: {
    getToday: () => apiClient.get('/api/recommendations/today'),
    follow: (id: string, followed: boolean) => 
      apiClient.patch(`/api/recommendations/${id}`, { followed }),
  },
};
