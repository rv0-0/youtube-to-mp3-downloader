import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Download, Files, CheckCircle } from 'lucide-react';

const StatusCard = ({ serverStatus, tasksCount, filesCount, activeDownloads }) => {
  const stats = [
    {
      icon: Activity,
      label: 'Server Status',
      value: serverStatus === 'online' ? 'Online' : serverStatus === 'offline' ? 'Offline' : 'Checking',
      color: serverStatus === 'online' ? 'text-green-400' : serverStatus === 'offline' ? 'text-red-400' : 'text-yellow-400',
      bgColor: serverStatus === 'online' ? 'bg-green-500/10' : serverStatus === 'offline' ? 'bg-red-500/10' : 'bg-yellow-500/10'
    },
    {
      icon: Download,
      label: 'Active Downloads',
      value: activeDownloads,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'
    },
    {
      icon: CheckCircle,
      label: 'Total Tasks',
      value: tasksCount,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    {
      icon: Files,
      label: 'Downloaded Files',
      value: filesCount,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.05 }}
          className="glass rounded-xl p-6 card-hover"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm font-medium mb-1">
                {stat.label}
              </p>
              <p className={`text-2xl font-bold ${stat.color}`}>
                {stat.value}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default StatusCard;
