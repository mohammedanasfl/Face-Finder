import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import UploadFace from '../components/UploadFace';
import UploadEventImages from '../components/UploadEventImages';
import ImageGrid from '../components/ImageGrid';
import { getRole } from '../services/authService';

const DashboardPage = () => {
    const [matches, setMatches] = useState([]);
    const role = getRole();

    return (
        <div className="app-container">
            <Navbar />

            <div className="dashboard-content">
                <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>

                    {/* Render Admin Bulk Uploader ONLY if User is Admin */}
                    {role === 'admin' && (
                        <div style={{ flex: '1 1 400px' }}>
                            <UploadEventImages />
                        </div>
                    )}

                    {/* Render Face Search Feature ONLY if User is a Standard User */}
                    {role === 'user' && (
                        <div style={{ flex: '1 1 500px' }}>
                            <UploadFace onSearchComplete={setMatches} />
                        </div>
                    )}

                </div>

                {/* Display Results ONLY if User is a Standard User */}
                {role === 'user' && <ImageGrid matches={matches} />}
            </div>
        </div>
    );
};

export default DashboardPage;
