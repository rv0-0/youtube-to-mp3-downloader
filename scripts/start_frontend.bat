@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              React Frontend Launcher                        ║
echo ║           YouTube to MP3 Downloader                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to frontend directory
cd /d "%~dp0..\frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ❌ Error: Dependencies not installed.
    echo Please run setup_frontend.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo 🚀 Starting React development server...
echo.
echo 🌐 Frontend will be available at: http://localhost:3000
echo 📡 Make sure API server is running at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start

echo.
echo 👋 Frontend stopped. Press any key to exit.
pause
