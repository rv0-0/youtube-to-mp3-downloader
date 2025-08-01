import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import DownloadForm from './components/DownloadForm';
import TaskList from './components/TaskList';
import FileManager from './components/FileManager';
import StatusCard from './components/StatusCard';
import { apiService } from './services/api';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('download');
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [serverStatus, setServerStatus] = useState('checking');
  const [loading, setLoading] = useState(false);

  // Check server health
  useEffect(() => {
    checkServerHealth();
    const interval = setInterval(checkServerHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Fetch tasks and files
  useEffect(() => {
    if (serverStatus === 'online') {
      fetchTasks();
      fetchFiles();
      const interval = setInterval(() => {
        fetchTasks();
        fetchFiles();
      }, 2000); // Update every 2 seconds
      return () => clearInterval(interval);
    }
  }, [serverStatus]);

  const checkServerHealth = async () => {
    try {
      await apiService.healthCheck();
      setServerStatus('online');
    } catch (error) {
      console.error('Server health check failed:', error);
      setServerStatus('offline');
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await apiService.getAllTasks();
      setTasks(response.tasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await apiService.getFiles();
      setFiles(response.files || []);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };

  const handleDownload = async (downloadData) => {
    setLoading(true);
    try {
      if (downloadData.isBatch) {
        await apiService.batchDownload(
          downloadData.urls,
          downloadData.quality,
          downloadData.mode,
          downloadData.maxWorkers
        );
      } else {
        await apiService.downloadVideo(
          downloadData.url,
          downloadData.quality,
          downloadData.mode
        );
      }
      fetchTasks(); // Refresh tasks immediately
    } catch (error) {
      console.error('Download failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleFileDelete = async (filename) => {
    try {
      await apiService.deleteFile(filename);
      fetchFiles(); // Refresh files list
    } catch (error) {
      console.error('Failed to delete file:', error);
      throw error;
    }
  };

  const tabVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          },
        }}
      />
      
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
        <div className="absolute top-40 left-1/2 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        <Header serverStatus={serverStatus} />
        
        <main className="container mx-auto px-4 py-8">
          {/* Status Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <StatusCard 
              serverStatus={serverStatus}
              tasksCount={tasks.length}
              filesCount={files.length}
              activeDownloads={tasks.filter(task => task.status === 'downloading').length}
            />
          </motion.div>

          {/* Navigation Tabs */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="glass rounded-xl p-2">
              <nav className="flex space-x-2">
                {[
                  { id: 'download', label: '🎵 Download', icon: '⬇️' },
                  { id: 'tasks', label: '📋 Tasks', icon: '📊' },
                  { id: 'files', label: '📁 Files', icon: '💾' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-white/20 text-white shadow-lg'
                        : 'text-white/70 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </motion.div>

          {/* Tab Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              variants={tabVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'download' && (
                <DownloadForm 
                  onDownload={handleDownload}
                  loading={loading}
                  serverOnline={serverStatus === 'online'}
                />
              )}
              
              {activeTab === 'tasks' && (
                <TaskList 
                  tasks={tasks}
                  onRefresh={fetchTasks}
                />
              )}
              
              {activeTab === 'files' && (
                <FileManager 
                  files={files}
                  onDelete={handleFileDelete}
                  onRefresh={fetchFiles}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default App;
