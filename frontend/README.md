# 🎨 **React Frontend for YouTube to MP3 Downloader**

A beautiful, modern React frontend that connects to your YouTube to MP3 downloader API.

## ✨ **Features**

- 🎵 **Beautiful UI**: Modern glass-morphism design with smooth animations
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile
- 🎯 **Real-time Updates**: Live progress tracking and status updates
- 🚀 **Fast Performance**: Optimized React components with Framer Motion
- 🎨 **Tailwind CSS**: Utility-first styling with custom design system
- 🔄 **Auto-refresh**: Automatic data updates every 2 seconds
- 📊 **Task Management**: Monitor all downloads with detailed status
- 📁 **File Manager**: Browse, download, and delete MP3 files
- 🌙 **Dark Theme**: Beautiful gradient backgrounds with glass effects

## 🚀 **Quick Start**

### Prerequisites
- Node.js 16+ and npm
- Your YouTube to MP3 API server running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - API Server: http://localhost:8000

## 🛠️ **Development**

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Project Structure

```
frontend/
├── public/
│   ├── index.html              # HTML template
│   └── manifest.json           # PWA manifest
├── src/
│   ├── components/             # React components
│   │   ├── Header.js           # App header with status
│   │   ├── StatusCard.js       # Server status dashboard
│   │   ├── DownloadForm.js     # Main download interface
│   │   ├── TaskList.js         # Download progress tracking
│   │   └── FileManager.js      # File browsing and management
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.js                  # Main application component
│   ├── index.js                # React entry point
│   └── index.css               # Global styles with Tailwind
├── package.json                # Dependencies and scripts
├── tailwind.config.js          # Tailwind configuration
└── postcss.config.js           # PostCSS configuration
```

## 🎨 **Design System**

### Colors
- **Primary**: Blue gradient (for main actions)
- **Secondary**: Purple gradient (for secondary actions)
- **Success**: Green gradient (for success states)
- **Warning**: Yellow gradient (for warnings)
- **Error**: Red gradient (for errors)

### Components
- **Glass Morphism**: Semi-transparent cards with backdrop blur
- **Smooth Animations**: Framer Motion for fluid interactions
- **Responsive Grid**: Mobile-first responsive design
- **Custom Buttons**: Gradient buttons with hover effects
- **Progress Bars**: Animated progress indicators

## 🔌 **API Integration**

The frontend connects to your FastAPI backend with these endpoints:

- `GET /health` - Server health check
- `POST /download` - Single video download
- `POST /batch-download` - Multiple video download
- `GET /status/{task_id}` - Download progress
- `GET /tasks` - All download tasks
- `GET /files` - Downloaded files list
- `DELETE /files/{filename}` - Delete file
- `GET /download-file/{filename}` - Download file

## 🚀 **Production Build**

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Serve the built files:**
   - The `build/` folder contains optimized production files
   - Serve with any static file server (nginx, Apache, etc.)
   - Or use `serve -s build` for quick testing

## 📱 **Mobile Support**

- Fully responsive design
- Touch-friendly interface
- Mobile-optimized layouts
- PWA ready (Progressive Web App)

## 🔧 **Customization**

### Styling
- Edit `tailwind.config.js` for custom colors and animations
- Modify `src/index.css` for global styles
- Component styles are in individual files

### API Configuration
- Edit `src/services/api.js` to change API endpoints
- Modify base URL for different environments

## 🎯 **Features Overview**

### 📥 **Download Interface**
- Single video download with video info preview
- Batch download with multiple URLs
- Quality selection (64-320 kbps)
- Download mode selection (basic/advanced/smart)
- File upload for URL lists

### 📊 **Task Monitoring**
- Real-time progress bars
- Status indicators with icons
- Error message display
- Task filtering and sorting

### 📁 **File Management**
- File search and filtering
- Download to device
- Delete files from server
- File size and date information

### 🎨 **UI/UX**
- Beautiful animations and transitions
- Loading states and feedback
- Toast notifications
- Glass morphism effects
- Gradient backgrounds

## 🏆 **Technologies Used**

- **React 18** - Modern React with hooks
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Elegant notifications
- **Axios** - HTTP client for API calls

## 🎉 **What's Included**

✅ Modern, responsive React application  
✅ Beautiful glass-morphism design  
✅ Real-time download progress  
✅ File management system  
✅ Mobile-optimized interface  
✅ Production-ready build system  
✅ API integration layer  
✅ Toast notifications  
✅ Loading states and animations  
✅ Error handling and validation  

**Your YouTube to MP3 downloader now has a professional, modern frontend! 🎉**
