import axios from 'axios';
import toast from 'react-hot-toast';
import type {
  LoginRequest,
  TokenResponse,
  User,
  Notification,
  NotificationCreateInput,
  NotificationUpdateInput,
} from '../types/api';

// ─── Axios Instance ──────────────────────────────────────────────────────────
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request Interceptor: Inject JWT ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Response Interceptor: Global Error Handling ─────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          localStorage.removeItem('access_token');
          toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
          window.location.href = '/login';
          break;
        case 400: {
          const detail = data?.detail;
          if (typeof detail === 'string') {
            toast.error(detail);
          } else if (Array.isArray(detail)) {
            detail.forEach((err: { msg: string }) => toast.error(err.msg));
          } else {
            toast.error('Error de validación en los datos enviados.');
          }
          break;
        }
        case 404:
          toast.error('Recurso no encontrado.');
          break;
        default:
          toast.error('Error inesperado. Intenta de nuevo más tarde.');
      }
    } else if (error.request) {
      toast.error('No se pudo conectar con el servidor.');
    }

    return Promise.reject(error);
  }
);

// ─── Auth API ────────────────────────────────────────────────────────────────
export const authApi = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },
};

// ─── Notifications API ───────────────────────────────────────────────────────
export const notificationsApi = {
  getAll: async (): Promise<Notification[]> => {
    const response = await api.get<Notification[]>('/notifications/');
    return response.data;
  },

  getById: async (id: number): Promise<Notification> => {
    const response = await api.get<Notification>(`/notifications/${id}`);
    return response.data;
  },

  create: async (data: NotificationCreateInput): Promise<Notification> => {
    const response = await api.post<Notification>('/notifications/', data);
    return response.data;
  },

  update: async (id: number, data: NotificationUpdateInput): Promise<Notification> => {
    const response = await api.put<Notification>(`/notifications/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/notifications/${id}`);
  },
};
