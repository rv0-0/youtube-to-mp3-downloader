import React from 'react';
import { motion } from 'framer-motion';
import { Music, Wifi, WifiOff } from 'lucide-react';

const Header = ({ serverStatus }) => {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass border-b border-white/10"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <motion.div 
            className="flex items-center space-x-4"
            whileHover={{ scale: 1.05 }}
          >
            <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl shadow-lg">
              <Music className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                YouTube to MP3
              </h1>
              <p className="text-white/70 text-sm">
                Fast, Beautiful, Professional
              </p>
            </div>
          </motion.div>

          {/* Server Status */}
          <motion.div 
            className="flex items-center space-x-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              serverStatus === 'online' 
                ? 'bg-green-500/20 text-green-300' 
                : serverStatus === 'offline'
                ? 'bg-red-500/20 text-red-300'
                : 'bg-yellow-500/20 text-yellow-300'
            }`}>
              {serverStatus === 'online' ? (
                <>
                  <Wifi className="w-4 h-4" />
                  <span className="text-sm font-medium">Server Online</span>
                </>
              ) : serverStatus === 'offline' ? (
                <>
                  <WifiOff className="w-4 h-4" />
                  <span className="text-sm font-medium">Server Offline</span>
                </>
              ) : (
                <>
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm font-medium">Checking...</span>
                </>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
