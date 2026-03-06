import api from './api';

export const searchFaces = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/search-face', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data.matches;
};

export const adminUploadImages = async (files) => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    const response = await api.post('/admin/upload-images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
};
