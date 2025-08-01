import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Clock, CheckCircle, XCircle, Download, Loader } from 'lucide-react';

const TaskList = ({ tasks, onRefresh }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'downloading':
        return <Loader className="w-5 h-5 text-blue-400 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'border-green-500/50 bg-green-500/10';
      case 'failed':
        return 'border-red-500/50 bg-red-500/10';
      case 'downloading':
        return 'border-blue-500/50 bg-blue-500/10';
      default:
        return 'border-yellow-500/50 bg-yellow-500/10';
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
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
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <Download className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Download Tasks</h2>
              <p className="text-white/70">Monitor your download progress</p>
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

        {tasks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Download className="w-8 h-8 text-white/50" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No Downloads Yet</h3>
            <p className="text-white/70">Start downloading some videos to see them here!</p>
          </motion.div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {tasks.map((task, index) => (
              <motion.div
                key={task.task_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-6 rounded-xl border-2 card-hover ${getStatusColor(task.status)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      {getStatusIcon(task.status)}
                      <span className={`text-sm font-medium capitalize px-2 py-1 rounded ${
                        task.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                        task.status === 'failed' ? 'bg-red-500/20 text-red-300' :
                        task.status === 'downloading' ? 'bg-blue-500/20 text-blue-300' :
                        'bg-yellow-500/20 text-yellow-300'
                      }`}>
                        {task.status}
                      </span>
                    </div>

                    <h3 className="text-white font-semibold text-lg mb-2 truncate">
                      {task.title || task.url || 'Unknown Title'}
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-white/70">Quality</p>
                        <p className="text-white font-medium">{task.quality} kbps</p>
                      </div>
                      <div>
                        <p className="text-white/70">Mode</p>
                        <p className="text-white font-medium capitalize">{task.mode}</p>
                      </div>
                      <div>
                        <p className="text-white/70">Duration</p>
                        <p className="text-white font-medium">{formatDuration(task.duration)}</p>
                      </div>
                      <div>
                        <p className="text-white/70">Size</p>
                        <p className="text-white font-medium">{formatFileSize(task.file_size)}</p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    {task.status === 'downloading' && task.progress !== undefined && (
                      <div className="mt-4">
                        <div className="flex justify-between text-sm text-white/70 mb-2">
                          <span>Progress</span>
                          <span>{Math.round(task.progress)}%</span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-2">
                          <motion.div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full progress-bar"
                            initial={{ width: 0 }}
                            animate={{ width: `${task.progress}%` }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {task.status === 'failed' && task.error && (
                      <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-red-300 text-sm">{task.error}</p>
                      </div>
                    )}

                    {/* Success Message */}
                    {task.status === 'completed' && task.filename && (
                      <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <p className="text-green-300 text-sm">
                          Downloaded: <span className="font-medium">{task.filename}</span>
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="text-right">
                    <p className="text-white/70 text-xs">Task ID</p>
                    <p className="text-white/50 text-xs font-mono">
                      {task.task_id.slice(0, 8)}...
                    </p>
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

export default TaskList;
