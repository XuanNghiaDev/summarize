import { createContext, createElement, useContext, useState, useEffect, useCallback } from 'react';
import { login as loginService, register as registerService, logout as logoutService } from './authService';
import { userAPI } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await userAPI.getProfile();
      setUser(response.data);
      setIsAuthenticated(true);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
      setError(err.response?.data?.detail || 'Failed to load user profile');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(
    async (email, password, fullName) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await registerService({ email, password, full_name: fullName });
        const { access_token, refresh_token } = response.data;
        
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        await fetchUserProfile();
        return response.data;
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Registration failed';
        setError(errorMsg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [fetchUserProfile]
  );

  const login = useCallback(
    async (email, password) => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await loginService({ email, password });
        const { access_token, refresh_token } = response.data;
        
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        await fetchUserProfile();
        return response.data;
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Login failed';
        setError(errorMsg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [fetchUserProfile]
  );

  const logout = useCallback(async () => {
    try {
      await logoutService();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
    }
  }, []);

  const updateProfile = useCallback(
    async (data) => {
      try {
        setIsLoading(true);
        setError(null);
        await userAPI.updateProfile(data);
        await fetchUserProfile();
      } catch (err) {
        const errorMsg = err.response?.data?.detail || 'Failed to update profile';
        setError(errorMsg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [fetchUserProfile]
  );

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    register,
    login,
    logout,
    updateProfile,
    refetchProfile: fetchUserProfile,
  };

  return createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
