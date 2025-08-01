@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║        YouTube to MP3 Downloader - Full Stack Launch       ║
echo ║              Backend + Frontend Together                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to project root
cd /d "%~dp0.."

echo 🔍 Checking prerequisites...

REM Check if Python virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Error: Python virtual environment not found.
    echo Please run the setup first.
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo ❌ Error: Frontend dependencies not installed.
    echo Please run scripts\setup_frontend.bat first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!
echo.

echo 🚀 Starting services...
echo.

REM Start API server in background
echo 📡 Starting API server (http://localhost:8000)...
start "YouTube to MP3 API Server" cmd /k ".venv\Scripts\python.exe src\api_server.py"

REM Wait a moment for API server to start
timeout /t 3 /nobreak >nul

REM Start React frontend
echo 🌐 Starting React frontend (http://localhost:3000)...
cd frontend
start "YouTube to MP3 Frontend" cmd /k "npm start"

echo.
echo ✅ Both services are starting!
echo.
echo 🌐 React Frontend: http://localhost:3000
echo 📡 API Server: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 💡 Both services will open in separate windows.
echo    Close those windows to stop the services.
echo.
echo Press any key to exit this launcher...
pause
