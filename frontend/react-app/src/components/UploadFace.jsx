import React, { useState } from 'react';
import { searchFaces } from '../services/faceService';
import Loader from './Loader';

const UploadFace = ({ onSearchComplete }) => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setError('');
            onSearchComplete([]); // Clear previous matches
        }
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setError('');
        onSearchComplete([]);
    };

    const handleSearch = async () => {
        if (!file) return;
        setLoading(true);
        setError('');

        try {
            const matches = await searchFaces(file);
            onSearchComplete(matches);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error searching faces');
            onSearchComplete([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="upload-card">
            <div className="upload-card-header">
                <h2 className="upload-card-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a888ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
                    Upload Face Photo
                </h2>
                <p className="upload-text">Upload a clear, well-lit photo of a face to find all matching event images.</p>
            </div>

            {!file ? (
                <label className="upload-dropzone">
                    <input type="file" accept="image/*" onChange={handleFileChange} />
                    <div className="upload-icon-box">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" /></svg>
                    </div>
                    <div className="upload-text">
                        <span className="upload-highlight">Click to upload</span> or drag & drop
                    </div>
                    <div className="upload-info">PNG, JPG, WEBP up to 10 MB</div>
                </label>
            ) : (
                <div className="upload-filled">
                    <div className="upload-preview-wrapper">
                        <img src={preview} alt="Upload preview" className="upload-preview" />
                        <div className="upload-preview-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2" /><path d="M17 3h2a2 2 0 0 1 2 2v2" /><path d="M21 17v2a2 2 0 0 1-2 2h-2" /><path d="M7 21H5a2 2 0 0 1-2-2v-2" /><path d="M9 9h.01" /><path d="M15 9h.01" /><path d="M10 14a3 3 0 0 0 4 0" /></svg>
                        </div>
                    </div>
                    <div className="upload-details">
                        <div className="upload-details-title">Face photo ready</div>
                        <div className="upload-text" style={{ marginBottom: '10px' }}>Image loaded — ready to search</div>
                        <div className="upload-actions" onClick={clearFile}>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" /><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" /><path d="M16 21v-5h5" /></svg>
                            Change photo
                        </div>
                    </div>
                    <div className="upload-actions" style={{ marginLeft: 'auto', alignSelf: 'flex-start' }} onClick={clearFile}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
                    </div>
                </div>
            )}

            <button
                className="btn btn-primary"
                style={{ marginTop: '24px' }}
                onClick={handleSearch}
                disabled={!file || loading}
            >
                {loading ? <Loader /> : (
                    <>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
                        Search Photos
                    </>
                )}
            </button>
            {error && <p style={{ color: '#ff5c5c', marginTop: '16px', textAlign: 'center' }}>{error}</p>}
        </div>
    );
};

export default UploadFace;
