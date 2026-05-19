import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';
const AI_API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:5000';

// ==================== API Client Setup ====================
export const backendAPI = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const aiAPI = axios.create({
  baseURL: AI_API_BASE_URL,
  timeout: 20000,
});

// Add JWT token interceptor
backendAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
backendAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return backendAPI(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// ==================== Authentication ====================
export const authAPI = {
  register: async (email, password, fullName) =>
    backendAPI.post('/auth/register', { email, password, full_name: fullName }),
  
  login: async (email, password) =>
    backendAPI.post('/auth/login', { email, password }),
  
  logout: () => backendAPI.post('/auth/logout'),
  
  refreshToken: async (refreshToken) =>
    backendAPI.post('/auth/refresh', { refresh_token: refreshToken }),
};

// ==================== User Profile ====================
export const userAPI = {
  getProfile: () => backendAPI.get('/user/profile'),
  
  updateProfile: async (data) =>
    backendAPI.put('/user/profile', data),
  
  getPublicProfile: (userId) =>
    backendAPI.get(`/user/profile/${userId}`),
};

// ==================== Quiz ====================
export const quizAPI = {
  submit: async (data) =>
    backendAPI.post('/quiz/submit', data),
  
  getHistory: async (page = 1, pageSize = 10, filters = {}) =>
    backendAPI.get('/quiz/history', { params: { page, page_size: pageSize, ...filters } }),
  
  getDetail: (quizId) =>
    backendAPI.get(`/quiz/history/${quizId}`),
  
  delete: (quizId) =>
    backendAPI.delete(`/quiz/history/${quizId}`),
};

// ==================== Summary ====================
export const summaryAPI = {
  save: async (data) =>
    backendAPI.post('/summary/save', data),
  
  getList: async (page = 1, pageSize = 10, filters = {}) =>
    backendAPI.get('/summary/list', { params: { page, page_size: pageSize, ...filters } }),
  
  getDetail: (summaryId) =>
    backendAPI.get(`/summary/${summaryId}`),
  
  toggleFavorite: (summaryId) =>
    backendAPI.put(`/summary/${summaryId}/favorite`),
  
  delete: (summaryId) =>
    backendAPI.delete(`/summary/${summaryId}`),
};

// ==================== Analytics ====================
export const analyticsAPI = {
  getDashboard: () =>
    backendAPI.get('/analytics/dashboard'),
  
  getUserAnalytics: () =>
    backendAPI.get('/analytics/user'),
  
  getPerformanceByCategory: () =>
    backendAPI.get('/analytics/performance/by-category'),
  
  getPerformanceByDifficulty: () =>
    backendAPI.get('/analytics/performance/by-difficulty'),
  
  getDailyPerformance: async (days = 30) =>
    backendAPI.get('/analytics/performance/daily', { params: { days } }),
  
  getStreak: () =>
    backendAPI.get('/analytics/streak'),
};

// ==================== Leaderboard ====================
export const leaderboardAPI = {
  getGlobal: async (limit = 50) =>
    backendAPI.get('/leaderboard/', { params: { limit } }),
  
  getByScore: async (limit = 50) =>
    backendAPI.get('/leaderboard/by-score', { params: { limit } }),
  
  getByQuizzes: async (limit = 50) =>
    backendAPI.get('/leaderboard/by-quizzes', { params: { limit } }),
  
  rebuild: () =>
    backendAPI.post('/leaderboard/rebuild'),
};

// ==================== Bookmarks ====================
export const bookmarksAPI = {
  create: async (data) =>
    backendAPI.post('/bookmarks', data),
  
  getList: async (page = 1, pageSize = 20, tag = null) =>
    backendAPI.get('/bookmarks', { params: { page, page_size: pageSize, tag } }),
  
  getDetail: (bookmarkId) =>
    backendAPI.get(`/bookmarks/${bookmarkId}`),
  
  update: async (bookmarkId, data) =>
    backendAPI.put(`/bookmarks/${bookmarkId}`, data),
  
  delete: (bookmarkId) =>
    backendAPI.delete(`/bookmarks/${bookmarkId}`),
};

export default backendAPI;
