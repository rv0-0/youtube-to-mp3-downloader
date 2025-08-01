@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           YouTube to MP3 Complete Test Suite                ║
echo ║              Unit Tests + API Tests                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set "python_exe=.\.venv\Scripts\python.exe"

REM Change to parent directory (project root)
cd /d "%~dp0.."

REM Check if Python virtual environment exists
if not exist "%python_exe%" (
    echo ❌ Error: Python virtual environment not found.
    echo Please run the setup first or check your installation.
    pause
    exit /b 1
)

echo 🧪 Complete Test Suite Options:
echo.
echo 1. Unit Tests Only (Fast - 30 seconds)
echo 2. API Tests Only (Requires running server)
echo 3. Full Test Suite (Unit + API tests)
echo 4. Quick API Tests (No downloads)
echo 5. Cancel
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🔬 Running Unit Tests...
    echo Testing core functions and validation logic.
    echo.
    "%python_exe%" tests/test_units.py
    echo.
    echo ✅ Unit tests completed!
    
) else if "%choice%"=="2" (
    echo.
    echo 📡 Running API Tests...
    echo Make sure the API server is running!
    echo You can start it with: start_api_server.bat
    echo.
    pause
    "%python_exe%" test_api.py
    echo.
    echo ✅ API tests completed!
    
) else if "%choice%"=="3" (
    echo.
    echo 🎯 Running Full Test Suite...
    echo This will run both unit tests and API tests.
    echo.
    echo Step 1/2: Unit Tests
    echo ==================
    "%python_exe%" test_units.py
    echo.
    echo Step 2/2: API Tests
    echo ==================
    echo Make sure the API server is running!
    echo You can start it with: start_api_server.bat
    echo.
    pause
    "%python_exe%" test_api.py
    echo.
    echo ✅ Full test suite completed!
    
) else if "%choice%"=="4" (
    echo.
    echo ⚡ Running Quick Tests...
    echo Unit tests + Quick API tests (no downloads).
    echo.
    echo Step 1/2: Unit Tests
    echo ==================
    "%python_exe%" test_units.py
    echo.
    echo Step 2/2: Quick API Tests
    echo ========================
    echo Make sure the API server is running!
    pause
    "%python_exe%" test_api.py --quick
    echo.
    echo ✅ Quick test suite completed!
    
) else if "%choice%"=="5" (
    echo 🚪 Cancelled by user.
    goto :end
    
) else (
    echo ❌ Invalid choice. Please run the script again.
    goto :end
)

echo.
echo 📊 Test Results Summary:
echo =====================
if exist "test_results.json" (
    echo ✅ API test results saved to: test_results.json
)
echo 💾 Check console output above for detailed results.
echo.
echo 🎉 Testing completed! Thank you for running the test suite.

:end
pause
