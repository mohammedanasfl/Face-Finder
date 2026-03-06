import React from 'react';

const ImageCard = ({ filename, onClick }) => {
    return (
        <div className="grid-item" onClick={onClick}>
            <img
                src={`http://127.0.0.1:8000/raw_images/${filename}`}
                alt={filename}
                className="grid-item-img"
                loading="lazy"
            />
            <div className="grid-item-footer">
                <span className="grid-item-name">{filename}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
            </div>
        </div>
    );
};

export default ImageCard;
