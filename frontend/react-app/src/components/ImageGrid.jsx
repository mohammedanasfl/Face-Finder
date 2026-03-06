import React, { useState, useEffect } from 'react';
import ImageCard from './ImageCard';

const ImageGrid = ({ matches }) => {
    const [selectedImage, setSelectedImage] = useState(null);

    // Close lightbox on Escape key
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') setSelectedImage(null);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    if (!matches || matches.length === 0) return null;

    return (
        <div style={{ marginTop: '40px' }}>
            <div className="results-header">
                <h2 className="results-title">Matches Found</h2>
                <span className="results-count">{matches.length} Photos</span>
            </div>

            <div className="grid">
                {matches.map((match, idx) => (
                    <ImageCard
                        key={idx}
                        filename={match}
                        onClick={() => setSelectedImage(match)}
                    />
                ))}
            </div>

            {/* Lightbox Overlay */}
            {selectedImage && (
                <div className="lightbox-overlay" onClick={() => setSelectedImage(null)}>
                    <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
                        <button className="lightbox-close" onClick={() => setSelectedImage(null)}>
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                        <img
                            src={`http://127.0.0.1:8000/raw_images/${selectedImage}`}
                            alt={selectedImage}
                            className="lightbox-img"
                        />
                        <div className="lightbox-footer">
                            {selectedImage}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImageGrid;
