import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Download single video
  async downloadVideo(url, quality = 192, mode = 'smart') {
    const response = await api.post('/download', {
      url,
      quality,
      mode,
    });
    return response.data;
  },

  // Batch download
  async batchDownload(urls, quality = 192, mode = 'smart', maxWorkers = 3) {
    const response = await api.post('/batch-download', {
      urls,
      quality,
      mode,
      max_workers: maxWorkers,
    });
    return response.data;
  },

  // Get download status
  async getStatus(taskId) {
    const response = await api.get(`/status/${taskId}`);
    return response.data;
  },

  // Get all tasks
  async getAllTasks() {
    const response = await api.get('/tasks');
    return response.data;
  },

  // Get video info
  async getVideoInfo(url) {
    const response = await api.get('/info', { params: { url } });
    return response.data;
  },

  // Get downloaded files
  async getFiles() {
    const response = await api.get('/files');
    return response.data;
  },

  // Download file
  async downloadFile(filename) {
    const response = await api.get(`/download-file/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete file
  async deleteFile(filename) {
    const response = await api.delete(`/files/${filename}`);
    return response.data;
  },

  // Upload URLs file
  async uploadUrls(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload-urls', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;
