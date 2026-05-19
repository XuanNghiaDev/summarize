import axios from 'axios';

export const aiAPI = axios.create({
  baseURL: import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:5000',
  timeout: 20000,
});
