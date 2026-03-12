import api from './api';

export const searchFaces = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/search-face', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
};

export const uploadAdminImages = async (files) => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await api.post('/admin/upload-images', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || 'Admin upload failed';
    }
};

export const importFromDrive = async (folderId) => {
    try {
        const response = await api.post('/admin/import-drive', {
            drive_folder_id: folderId
        });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || 'Failed to start Drive import';
    }
};

export const getJobStatus = async (jobId) => {
    try {
        const response = await api.get(`/admin/job-status/${jobId}`);
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || 'Failed to get job status';
    }
};
