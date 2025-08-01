@echo off
echo 🚀 Deploying YouTube Downloader to Vercel...
echo.

echo 📝 Step 1: Installing Vercel CLI (if not installed)
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
) else (
    echo ✅ Vercel CLI already installed
)

echo.
echo 📦 Step 2: Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ❌ Frontend dependency installation failed
    exit /b 1
)

echo.
echo 🏗️ Step 3: Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Frontend build failed
    exit /b 1
)

echo.
echo 📤 Step 4: Deploying to Vercel...
cd ..
vercel --prod

echo.
echo ✅ Deployment complete!
echo 📖 Visit your Vercel dashboard to see the deployment status
echo 🌐 Your app will be available at the URL provided by Vercel

pause
