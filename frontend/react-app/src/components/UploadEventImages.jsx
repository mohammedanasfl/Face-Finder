import React, { useEffect, useState } from 'react';
import { getJobStatus, uploadAdminImages } from '../services/faceService';
import Loader from './Loader';

const UploadEventImages = () => {
    const [files, setFiles] = useState([]);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files.length > 0) {
            setFiles(Array.from(e.target.files));
            setError('');
            setStatus(null);
        }
    };

    const handleUpload = async () => {
        if (!files || files.length === 0) return;
        setLoading(true);
        setError('');
        setStatus(null);

        try {
            const result = await uploadAdminImages(files);
            setJobId(result.job_id);
            setStatus(result);
            setFiles([]);
        } catch (err) {
            setError(err?.response?.data?.detail || err || 'Error uploading images');
            setLoading(false);
        }
    };

    useEffect(() => {
        let intervalId;

        const pollStatus = async () => {
            if (!jobId) return;
            try {
                const response = await getJobStatus(jobId);
                setStatus(response);
                if (response.status === 'completed' || response.status === 'failed' || response.status === 'completed_no_images') {
                    setLoading(false);
                    clearInterval(intervalId);
                }
            } catch {
                setError('Lost connection to upload job.');
                setLoading(false);
                clearInterval(intervalId);
            }
        };

        if (jobId && loading) {
            pollStatus();
            intervalId = setInterval(pollStatus, 3000);
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [jobId, loading]);

    return (
        <div className="upload-card">
            <div className="upload-card-header">
                <h2 className="upload-card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#28a745" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line></svg>
                    [Admin] Bulk Image Upload
                </h2>
                <p className="upload-text">Upload new event photos. The AI will process them in a background job and rebuild the index safely.</p>
            </div>

            <label className="upload-dropzone">
                <input type="file" accept="image/*" multiple onChange={handleFileChange} />
                <div className="upload-icon-box">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                </div>
                <div className="upload-text">
                    <span className="upload-highlight">Select multiple files</span> or drag & drop
                </div>
                {files.length > 0 && <div className="upload-info" style={{ color: '#a888ff' }}>{files.length} files selected</div>}
            </label>

            <button
                className="btn btn-outline"
                style={{ marginTop: '24px', width: '100%', borderColor: '#28a745', color: '#28a745' }}
                onClick={handleUpload}
                disabled={files.length === 0 || loading}
            >
                {loading ? <Loader /> : (
                    <>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 16 12 12 8 16"></polyline><line x1="12" y1="12" x2="12" y2="21"></line><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"></path><polyline points="16 16 12 12 8 16"></polyline></svg>
                        Upload & Queue Index Job ({files.length})
                    </>
                )}
            </button>

            {error && <p style={{ color: '#ff5c5c', marginTop: '16px', textAlign: 'center' }}>{error}</p>}
            {status && (
                <div style={{ marginTop: '16px', padding: '12px', borderRadius: '12px', backgroundColor: 'var(--bg-input)' }}>
                    <p style={{ margin: 0, color: 'white' }}>Status: {status.status}</p>
                    <p style={{ margin: '8px 0 0', color: 'var(--text-muted)' }}>Images received: {status.images_received || 0}</p>
                    <p style={{ margin: '8px 0 0', color: 'var(--text-muted)' }}>Faces indexed: {status.faces_indexed || 0}</p>
                    {status.error && <p style={{ margin: '8px 0 0', color: '#ff5c5c' }}>{status.error}</p>}
                </div>
            )}
        </div>
    );
};

export default UploadEventImages;
