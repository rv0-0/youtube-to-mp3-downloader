@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              React Frontend Setup                           ║
echo ║           YouTube to MP3 Downloader                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to frontend directory
cd /d "%~dp0..\frontend"

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Node.js is not installed or not in PATH.
    echo Please download and install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check Node.js version
echo 🔍 Checking Node.js version...
node --version
echo.

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ Error: package.json not found.
    echo Please make sure you're in the frontend directory.
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
echo This may take a few minutes...
echo.

REM Install dependencies
npm install

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Error: Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ✅ Frontend setup completed successfully!
echo.
echo 🚀 To start the development server:
echo    npm start
echo.
echo 🌐 The frontend will be available at:
echo    http://localhost:3000
echo.
echo 💡 Make sure your API server is running on http://localhost:8000
echo.
pause
