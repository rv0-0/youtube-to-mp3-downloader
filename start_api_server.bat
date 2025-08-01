@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              YouTube to MP3 API Server                      ║
echo ║                   Starting FastAPI...                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set "python_exe=.\.venv\Scripts\python.exe"

REM Check if Python virtual environment exists
if not exist "%python_exe%" (
    echo ❌ Error: Python virtual environment not found.
    echo Please run the setup first or check your installation.
    pause
    exit /b 1
)

echo 🚀 Starting FastAPI server on http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🌐 Web Interface: Open web_interface.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

"%python_exe%" -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 👋 Server stopped. Press any key to exit.
pause
