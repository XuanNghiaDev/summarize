import { backendAPI } from './backendAPI';

export const register = (data) =>
  backendAPI.post('/auth/register', data);

export const login = (data) => backendAPI.post('/auth/login', data);

export const logout = () => backendAPI.post('/auth/logout');

export const refreshToken = (data) =>
  backendAPI.post('/auth/refresh', data);
