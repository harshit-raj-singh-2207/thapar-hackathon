import apiClient from './apiClient';

export const authApi = {
  login: ({ email, password }) => apiClient.post('/auth/login', { email, password }),
  register: (data) => apiClient.post('/auth/register', data),
  forgotPassword: ({ email }) => apiClient.post('/auth/forgot-password', { email }),
};
