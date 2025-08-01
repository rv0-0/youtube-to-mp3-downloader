import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Files, Download, Trash2, RefreshCw, Search, Music } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';

const FileManager = ({ files, onDelete, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [downloading, setDownloading] = useState(new Set());

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const handleDownload = async (filename) => {
    setDownloading(new Set([...downloading, filename]));
    try {
      const blob = await apiService.downloadFile(filename);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Downloaded ${filename}`);
    } catch (error) {
      console.error('Download failed:', error);
      toast.error(`Failed to download ${filename}`);
    } finally {
      setDownloading(new Set([...downloading].filter(f => f !== filename)));
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      await onDelete(filename);
      toast.success(`Deleted ${filename}`);
    } catch (error) {
      console.error('Delete failed:', error);
      toast.error(`Failed to delete ${filename}`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto"
    >
      <div className="glass rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg">
              <Files className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Downloaded Files</h2>
              <p className="text-white/70">Manage your MP3 collection</p>
            </div>
          </div>
          
          <motion.button
            onClick={onRefresh}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </motion.button>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/50" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search files..."
              className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent input-focus"
            />
          </div>
        </div>

        {/* Files Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-white/70 text-sm">Total Files</p>
            <p className="text-2xl font-bold text-white">{files.length}</p>
          </div>
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-white/70 text-sm">Total Size</p>
            <p className="text-2xl font-bold text-white">
              {formatFileSize(files.reduce((total, file) => total + (file.size || 0), 0))}
            </p>
          </div>
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-white/70 text-sm">Filtered Results</p>
            <p className="text-2xl font-bold text-white">{filteredFiles.length}</p>
          </div>
        </div>

        {filteredFiles.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Music className="w-8 h-8 text-white/50" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {files.length === 0 ? 'No Files Yet' : 'No Files Found'}
            </h3>
            <p className="text-white/70">
              {files.length === 0 
                ? 'Start downloading some videos to see them here!'
                : 'Try adjusting your search terms.'
              }
            </p>
          </motion.div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredFiles.map((file, index) => (
              <motion.div
                key={file.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all card-hover"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1 min-w-0">
                    <div className="p-2 bg-gradient-to-r from-pink-500 to-rose-500 rounded-lg">
                      <Music className="w-5 h-5 text-white" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-medium truncate mb-1">
                        {file.name}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-white/70">
                        <span>{formatFileSize(file.size)}</span>
                        <span>{formatDate(file.modified)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <motion.button
                      onClick={() => handleDownload(file.name)}
                      disabled={downloading.has(file.name)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Download file"
                    >
                      {downloading.has(file.name) ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Download className="w-4 h-4" />
                      )}
                    </motion.button>

                    <motion.button
                      onClick={() => handleDelete(file.name)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                      title="Delete file"
                    >
                      <Trash2 className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default FileManager;
