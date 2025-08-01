@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              YouTube to MP3 API Test Suite                  ║
echo ║                 Testing All Endpoints                       ║
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

echo 🧪 Starting API Test Suite...
echo.
echo Make sure the API server is running before starting tests!
echo You can start it with: start_api_server.bat
echo.
echo Choose test mode:
echo 1. Full Test Suite (includes downloads) - Takes 3-5 minutes
echo 2. Quick Tests (no downloads) - Takes 30 seconds
echo 3. Cancel
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🔄 Running full test suite...
    echo This will test all endpoints including actual downloads.
    echo Please be patient, this may take several minutes.
    echo.
    "%python_exe%" test_api.py
) else if "%choice%"=="2" (
    echo.
    echo ⚡ Running quick tests...
    echo Testing connectivity and basic endpoints only.
    echo.
    "%python_exe%" test_api.py --quick
) else if "%choice%"=="3" (
    echo 🚪 Cancelled by user.
    goto :end
) else (
    echo ❌ Invalid choice. Please run the script again.
    goto :end
)

echo.
echo ✅ Tests completed!
echo 📊 Check test_results.json for detailed results.
echo.

:end
pause
