import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, isAuthenticated } from '../services/authService';
import Loader from '../components/Loader';

const LoginPage = () => {
    const [secretKey, setSecretKey] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Redirect if already logged in
        if (isAuthenticated()) {
            navigate('/dashboard');
        }
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(secretKey);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid secret key');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-layout">
            <div className="login-bg"></div>

            <form onSubmit={handleSubmit} className="login-card">
                <div className="logo-container">
                    <div className="logo-box">
                        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 7V5a2 2 0 0 1 2-2h2" />
                            <path d="M17 3h2a2 2 0 0 1 2 2v2" />
                            <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
                            <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
                            <path d="M9 10h.01" className="eye-left" />
                            <path d="M15 10h.01" className="eye-right" />
                            <path d="M10 14a3 3 0 0 0 4 0" className="mouth" />
                        </svg>
                    </div>
                </div>

                <div className="pill">AI Facial Recognition</div>

                <h1 className="title">FaceFind Access</h1>
                <p className="subtitle">Enter your secret key to continue</p>

                <div className="input-group" style={{ marginTop: '32px' }}>
                    <label className="input-label">Secret Key</label>
                    <div className="input-wrapper">
                        <svg className="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
                        <input
                            type="password"
                            className="input-field"
                            placeholder="Enter Key..."
                            value={secretKey}
                            onChange={(e) => setSecretKey(e.target.value)}
                            required
                        />
                    </div>
                </div>

                <button type="submit" className="btn btn-primary" disabled={loading || !secretKey}>
                    {loading ? <Loader /> : 'Secure Login'}
                </button>

                {error && <p style={{ color: '#ff5c5c', marginTop: '16px' }}>{error}</p>}
            </form>
        </div>
    );
};

export default LoginPage;
