import React, { useState, useEffect } from 'react';
import { importFromDrive, getJobStatus } from '../services/faceService';
import Loader from './Loader';

const ImportFromDrive = () => {
    const [driveFolderId, setDriveFolderId] = useState('');
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleImport = async (e) => {
        e.preventDefault();
        setError('');

        if (!driveFolderId.trim()) {
            setError('Please enter a Google Drive folder ID.');
            return;
        }

        setLoading(true);
        try {
            const data = await importFromDrive(driveFolderId);
            setJobId(data.job_id);
            setStatus(data);
        } catch (err) {
            setError(err.message || 'Failed to start import job.');
            setLoading(false);
        }
    };

    useEffect(() => {
        let intervalId;

        const checkStatus = async () => {
            if (!jobId) return;

            try {
                const data = await getJobStatus(jobId);
                setStatus(data);

                if (data.status === 'completed' || data.status === 'failed' || data.status === 'completed_no_images') {
                    clearInterval(intervalId);
                    setLoading(false);
                }
            } catch (err) {
                console.error('Failed to poll status', err);
                clearInterval(intervalId);
                setLoading(false);
                setError('Lost connection to background job.');
            }
        };

        if (jobId && loading) {
            checkStatus();
            intervalId = setInterval(checkStatus, 3000);
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [jobId, loading]);

    return (
        <div className="section-card">
            <h2 className="section-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                Import from Google Drive
            </h2>
            <p className="section-subtitle">Automatically download and index all event photos from a public Google Drive folder.</p>

            <form onSubmit={handleImport} style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px' }}>
                <input
                    type="text"
                    className="input-field"
                    placeholder="Enter Google Drive Folder ID..."
                    value={driveFolderId}
                    onChange={(e) => setDriveFolderId(e.target.value)}
                    disabled={loading}
                    style={{ padding: '16px', borderRadius: '8px', fontSize: '15px' }}
                />

                <button type="submit" className="btn btn-primary" disabled={loading || !driveFolderId} style={{ padding: '16px', borderRadius: '8px', fontSize: '15px', fontWeight: 'bold' }}>
                    {loading && !jobId ? <Loader /> : 'Start Import Job'}
                </button>
            </form>

            {error && <p style={{ color: '#ff5c5c', marginTop: '16px', fontSize: '14px' }}>{error}</p>}

            {status && (
                <div style={{ marginTop: '24px', padding: '16px', backgroundColor: 'var(--bg-input)', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                        <span style={{ fontWeight: '600', color: 'var(--text-main)' }}>Background Job Status</span>
                        <span style={{
                            fontSize: '13px',
                            fontWeight: '600',
                            padding: '4px 8px',
                            borderRadius: '6px',
                            backgroundColor: status.status === 'completed' ? 'rgba(76, 175, 80, 0.15)' : (status.status === 'failed' ? 'rgba(244, 67, 54, 0.15)' : 'rgba(123, 77, 252, 0.15)'),
                            color: status.status === 'completed' ? '#4CAF50' : (status.status === 'failed' ? '#f44336' : 'var(--primary)')
                        }}>
                            {status.status.toUpperCase()}
                        </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '16px' }}>
                        <div style={{ padding: '12px', backgroundColor: 'var(--bg-dark)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Images Downloaded</div>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'white' }}>{status.images_downloaded || 0}</div>
                        </div>
                        <div style={{ padding: '12px', backgroundColor: 'var(--bg-dark)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Faces Indexed</div>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'white' }}>{status.faces_indexed || 0}</div>
                        </div>
                    </div>
                    {status.error && <p style={{ marginTop: '12px', color: '#ff5c5c' }}>{status.error}</p>}
                </div>
            )}
        </div>
    );
};

export default ImportFromDrive;
