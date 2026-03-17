import React from 'react';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const ImageCard = ({ match, onClick }) => {
    const imageUrl = `${BASE_URL}/raw_images/${match.filename}`;

    const handleDownload = async (e) => {
        e.stopPropagation(); // Don't open lightbox
        try {
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = match.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(blobUrl);
        } catch (err) {
            console.error('Download failed:', err);
        }
    };

    return (
        <div className="grid-item" onClick={onClick}>
            <img
                src={imageUrl}
                alt={match.filename}
                className="grid-item-img"
                loading="lazy"
            />
            <div className="grid-item-footer">
                <span className="grid-item-name">{match.filename} ({match.score})</span>
                <svg
                    onClick={handleDownload}
                    style={{ cursor: 'pointer' }}
                    width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="var(--text-muted)" strokeWidth="2"
                    strokeLinecap="round" strokeLinejoin="round"
                    title="Download image"
                >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
            </div>
        </div>
    );
};

export default ImageCard;
