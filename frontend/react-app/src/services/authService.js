import api from './api';

const parseJwt = (token) => {
    try {
        const [, payload] = token.split('.');
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
};

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
    const token = localStorage.getItem('token');
    if (!token) {
        return false;
    }

    const payload = parseJwt(token);
    if (!payload?.exp) {
        logout();
        return false;
    }

    const expiresAtMs = payload.exp * 1000;
    if (Date.now() >= expiresAtMs) {
        logout();
        return false;
    }

    return true;
};
