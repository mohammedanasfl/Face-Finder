import React, { useState } from 'react';
import { uploadAdminImages } from '../services/faceService';
import Loader from './Loader';

const UploadEventImages = () => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files.length > 0) {
            // Convert FileList to Array
            setFiles(Array.from(e.target.files));
            setError('');
            setSuccessMsg('');
        }
    };

    const handleUpload = async () => {
        if (!files || files.length === 0) return;
        setLoading(true);
        setError('');
        setSuccessMsg('');

        try {
            const result = await uploadAdminImages(files);
            setSuccessMsg(result.message);
            setFiles([]); // Clear selection after success
        } catch (err) {
            setError(err.response?.data?.detail || 'Error uploading images');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="upload-card">
            <div className="upload-card-header">
                <h2 className="upload-card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#28a745" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line></svg>
                    [Admin] Bulk Image Upload
                </h2>
                <p className="upload-text">Upload new event photos. The AI will automatically process the crops, generate embeddings, and rebuild the FAISS index.</p>
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
                        Upload & Add to FAISS Index ({files.length})
                    </>
                )}
            </button>

            {successMsg && <p style={{ color: '#28a745', marginTop: '16px', textAlign: 'center' }}>{successMsg}</p>}
            {error && <p style={{ color: '#ff5c5c', marginTop: '16px', textAlign: 'center' }}>{error}</p>}
        </div>
    );
};

export default UploadEventImages;
