import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getRole } from '../services/authService';

export const ProtectedRoute = ({ children, requireAdmin = false }) => {
    if (!isAuthenticated()) {
        return <Navigate to="/" replace />;
    }

    if (requireAdmin && getRole() !== 'admin') {
        // Redirect standard users away from admin-only routes
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};
