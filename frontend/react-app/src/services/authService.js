import api from './api';

export const login = async (secretKey) => {
    const response = await api.post('/login', { secret_key: secretKey });

    // Store credentials
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);

    return response.data;
};

export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
};

export const getRole = () => {
    return localStorage.getItem('role');
};

export const isAuthenticated = () => {
    return !!localStorage.getItem('token');
};
