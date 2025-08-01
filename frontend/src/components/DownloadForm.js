import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, Plus, Trash2, Upload, Info, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';

const DownloadForm = ({ onDownload, loading, serverOnline }) => {
  const [mode, setMode] = useState('single');
  const [url, setUrl] = useState('');
  const [urls, setUrls] = useState(['']);
  const [quality, setQuality] = useState(192);
  const [downloadMode, setDownloadMode] = useState('smart');
  const [maxWorkers, setMaxWorkers] = useState(3);
  const [videoInfo, setVideoInfo] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);

  const qualityOptions = [
    { value: 64, label: '64 kbps (Low)' },
    { value: 128, label: '128 kbps (Standard)' },
    { value: 192, label: '192 kbps (High)' },
    { value: 256, label: '256 kbps (Very High)' },
    { value: 320, label: '320 kbps (Maximum)' }
  ];

  const modeOptions = [
    { value: 'basic', label: 'Basic', description: 'Simple download' },
    { value: 'advanced', label: 'Advanced', description: 'Enhanced features' },
    { value: 'smart', label: 'Smart', description: 'AI-powered with duplicates detection' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!serverOnline) {
      toast.error('Server is offline. Please check your connection.');
      return;
    }

    try {
      const downloadData = {
        isBatch: mode === 'batch',
        quality: parseInt(quality),
        mode: downloadMode,
        maxWorkers: parseInt(maxWorkers)
      };

      if (mode === 'single') {
        if (!url.trim()) {
          toast.error('Please enter a YouTube URL');
          return;
        }
        downloadData.url = url.trim();
      } else {
        const validUrls = urls.filter(u => u.trim());
        if (validUrls.length === 0) {
          toast.error('Please enter at least one YouTube URL');
          return;
        }
        downloadData.urls = validUrls;
      }

      await onDownload(downloadData);
      toast.success(`${mode === 'single' ? 'Download' : 'Batch download'} started successfully!`);
      
      // Reset form
      setUrl('');
      setUrls(['']);
      setVideoInfo(null);
    } catch (error) {
      console.error('Download error:', error);
      toast.error(error.response?.data?.detail || 'Download failed. Please try again.');
    }
  };

  const handleGetInfo = async () => {
    if (!url.trim()) {
      toast.error('Please enter a YouTube URL first');
      return;
    }

    setLoadingInfo(true);
    try {
      const info = await apiService.getVideoInfo(url.trim());
      setVideoInfo(info);
      toast.success('Video information loaded!');
    } catch (error) {
      console.error('Info error:', error);
      toast.error('Failed to get video information');
      setVideoInfo(null);
    } finally {
      setLoadingInfo(false);
    }
  };

  const addUrlField = () => {
    setUrls([...urls, '']);
  };

  const removeUrlField = (index) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const updateUrl = (index, value) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const response = await apiService.uploadUrls(file);
      setUrls(response.urls || []);
      toast.success(`Loaded ${response.urls?.length || 0} URLs from file`);
    } catch (error) {
      console.error('File upload error:', error);
      toast.error('Failed to upload file');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <div className="glass rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
            <Download className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white">Download YouTube Videos</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mode Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <motion.button
              type="button"
              onClick={() => setMode('single')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-xl border-2 transition-all ${
                mode === 'single'
                  ? 'border-blue-500 bg-blue-500/10 text-white'
                  : 'border-white/20 bg-white/5 text-white/70 hover:border-white/40'
              }`}
            >
              <div className="text-center">
                <Download className="w-8 h-8 mx-auto mb-2" />
                <h3 className="font-semibold">Single Download</h3>
                <p className="text-sm opacity-70">Download one video</p>
              </div>
            </motion.button>

            <motion.button
              type="button"
              onClick={() => setMode('batch')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-xl border-2 transition-all ${
                mode === 'batch'
                  ? 'border-purple-500 bg-purple-500/10 text-white'
                  : 'border-white/20 bg-white/5 text-white/70 hover:border-white/40'
              }`}
            >
              <div className="text-center">
                <Plus className="w-8 h-8 mx-auto mb-2" />
                <h3 className="font-semibold">Batch Download</h3>
                <p className="text-sm opacity-70">Download multiple videos</p>
              </div>
            </motion.button>
          </div>

          {/* Single URL Input */}
          {mode === 'single' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-4"
            >
              <div className="flex space-x-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent input-focus"
                  required
                />
                <motion.button
                  type="button"
                  onClick={handleGetInfo}
                  disabled={loadingInfo || !url.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingInfo ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Info className="w-5 h-5" />
                  )}
                </motion.button>
              </div>

              {/* Video Info Card */}
              {videoInfo && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="p-4 bg-white/5 border border-white/10 rounded-lg"
                >
                  <h4 className="font-semibold text-white mb-2">Video Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-white/70">Title:</p>
                      <p className="text-white font-medium">{videoInfo.title}</p>
                    </div>
                    <div>
                      <p className="text-white/70">Duration:</p>
                      <p className="text-white font-medium">{videoInfo.duration}</p>
                    </div>
                    <div>
                      <p className="text-white/70">Channel:</p>
                      <p className="text-white font-medium">{videoInfo.uploader}</p>
                    </div>
                    <div>
                      <p className="text-white/70">Views:</p>
                      <p className="text-white font-medium">{videoInfo.view_count?.toLocaleString()}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Batch URL Inputs */}
          {mode === 'batch' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">YouTube URLs</h3>
                <div className="flex space-x-2">
                  <label className="btn-secondary cursor-pointer">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload File
                    <input
                      type="file"
                      accept=".txt"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                  <motion.button
                    type="button"
                    onClick={addUrlField}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="btn-primary"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add URL
                  </motion.button>
                </div>
              </div>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                {urls.map((urlValue, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex space-x-2"
                  >
                    <input
                      type="url"
                      value={urlValue}
                      onChange={(e) => updateUrl(index, e.target.value)}
                      placeholder={`YouTube URL ${index + 1}`}
                      className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent input-focus"
                    />
                    {urls.length > 1 && (
                      <motion.button
                        type="button"
                        onClick={() => removeUrlField(index)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-3 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </motion.button>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Settings */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Quality */}
            <div>
              <label className="block text-white font-medium mb-2">Audio Quality</label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent input-focus"
              >
                {qualityOptions.map(option => (
                  <option key={option.value} value={option.value} className="bg-gray-800">
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Download Mode */}
            <div>
              <label className="block text-white font-medium mb-2">
                <Sparkles className="w-4 h-4 inline mr-1" />
                Download Mode
              </label>
              <select
                value={downloadMode}
                onChange={(e) => setDownloadMode(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent input-focus"
              >
                {modeOptions.map(option => (
                  <option key={option.value} value={option.value} className="bg-gray-800">
                    {option.label} - {option.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Workers (for batch) */}
            {mode === 'batch' && (
              <div>
                <label className="block text-white font-medium mb-2">Parallel Downloads</label>
                <select
                  value={maxWorkers}
                  onChange={(e) => setMaxWorkers(e.target.value)}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent input-focus"
                >
                  {[1, 2, 3, 4, 5].map(num => (
                    <option key={num} value={num} className="bg-gray-800">
                      {num} {num === 1 ? 'worker' : 'workers'}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={loading || !serverOnline}
            whileHover={{ scale: loading ? 1 : 1.02 }}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
              loading || !serverOnline
                ? 'bg-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 shadow-lg hover:shadow-xl'
            } text-white`}
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Starting Download...</span>
              </div>
            ) : !serverOnline ? (
              'Server Offline'
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <Download className="w-5 h-5" />
                <span>Start Download</span>
              </div>
            )}
          </motion.button>
        </form>
      </div>
    </motion.div>
  );
};

export default DownloadForm;
