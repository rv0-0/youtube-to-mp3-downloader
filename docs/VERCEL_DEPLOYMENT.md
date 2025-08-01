# Vercel Deployment Guide

## 🚀 Deploying to Vercel

This project is now structured for easy deployment to Vercel, which provides excellent hosting for both frontend and serverless backend functions.

### 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install with `npm install -g vercel`
3. **Git Repository**: Your code should be pushed to GitHub

### 🏗️ Project Structure for Vercel

```
📁 Project Root
├── 📁 api/                    # Serverless API functions
│   ├── index.py              # Main API entry point
│   ├── health.py             # Health check endpoint
│   └── download.py           # Download endpoint
├── 📁 frontend/              # React application
│   ├── build/                # Production build (generated)
│   ├── src/                  # Source code
│   └── package.json          # Dependencies
├── vercel.json               # Vercel configuration
└── requirements.txt          # Python dependencies
```

### 🛠️ Deployment Methods

#### Method 1: Automated Script
```bash
# Run the deployment script
scripts\deploy_vercel.bat
```

#### Method 2: Manual Deployment
```bash
# Install dependencies
cd frontend
npm install
npm run build
cd ..

# Deploy to Vercel
vercel --prod
```

#### Method 3: GitHub Integration
1. Push your code to GitHub
2. Connect your GitHub repo to Vercel
3. Automatic deployments on every push

### ⚙️ Configuration Files

#### `vercel.json`
- Configures build settings
- Routes API requests to serverless functions
- Serves frontend from React build

#### `requirements.txt`
- Python dependencies for API functions
- Optimized for Vercel's Python runtime

#### `frontend/.env.production`
- Production environment variables
- API URL configuration

### 🔧 API Endpoints

Once deployed, your API will be available at:
- `https://your-app.vercel.app/api/health` - Health check
- `https://your-app.vercel.app/api/download` - Download endpoint
- `https://your-app.vercel.app/api/` - Main API

### 🌐 Frontend

Your React app will be served from:
- `https://your-app.vercel.app/` - Main application

### ⚠️ Important Notes

1. **Serverless Limitations**: 
   - Functions have execution time limits (10s hobby, 60s pro)
   - File downloads might need to be handled differently
   - Consider using external storage for large files

2. **Environment Variables**:
   - Set any required environment variables in Vercel dashboard
   - API keys, database URLs, etc.

3. **Custom Domain**:
   - Add your custom domain in Vercel dashboard
   - Automatic HTTPS certificates

### 🐛 Troubleshooting

1. **Build Failures**: Check logs in Vercel dashboard
2. **API Errors**: Verify Python dependencies in `requirements.txt`
3. **CORS Issues**: API includes CORS middleware for all origins

### 📊 Monitoring

- View deployment logs in Vercel dashboard
- Monitor function execution and errors
- Analytics and performance metrics available

Happy deploying! 🎉
