import React from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/authService';

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className="navbar">
            <div className="dash-logo">
                <div className="dash-logo-box">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 7V5a2 2 0 0 1 2-2h2" />
                        <path d="M17 3h2a2 2 0 0 1 2 2v2" />
                        <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
                        <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
                        <path d="M9 10h.01" className="eye-left" />
                        <path d="M15 10h.01" className="eye-right" />
                        <path d="M10 14a3 3 0 0 0 4 0" className="mouth" />
                    </svg>
                </div>
                <div className="dash-title">
                    FaceFind <span className="dash-subtitle">Photo Search</span>
                </div>
            </div>
            <button className="btn btn-outline" onClick={handleLogout}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
                Sign out
            </button>
        </nav>
    );
};

export default Navbar;
