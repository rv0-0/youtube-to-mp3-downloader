@echo off
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 YouTube to MP3 Downloader                   ║
echo ║                    Universal Launcher                       ║
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

REM Show menu if no arguments provided
if "%~1"=="" goto :show_menu

REM Parse command line arguments
set "mode=%~1"
set "url_or_file=%~2"
set "quality=%~3"
set "workers=%~4"

if "%quality%"=="" set "quality=192"
if "%workers%"=="" set "workers=3"

goto :execute_mode

:show_menu
echo Select download mode:
echo.
echo 1. 🎵 Basic Download      - Simple single video download
echo 2. ⚡ Advanced Download   - Parallel downloads, resume, thumbnails
echo 3. 🧠 Smart Download     - AI-like features, duplicate detection
echo 4. 📋 Batch from File    - Download multiple URLs from text file
echo 5. 🔄 Resume Downloads   - Resume failed downloads
echo 6. 📊 Show Statistics    - View download history and stats
echo 7. ⚙️  Install FFmpeg     - Install FFmpeg for audio conversion
echo 8. ❓ Help              - Show detailed usage examples
echo 9. 🚪 Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto :basic_download
if "%choice%"=="2" goto :advanced_download
if "%choice%"=="3" goto :smart_download
if "%choice%"=="4" goto :batch_download
if "%choice%"=="5" goto :resume_download
if "%choice%"=="6" goto :show_stats
if "%choice%"=="7" goto :install_ffmpeg
if "%choice%"=="8" goto :show_help
if "%choice%"=="9" goto :exit
goto :invalid_choice

:basic_download
echo.
echo 🎵 Basic Download Mode
set /p url="Enter YouTube URL: "
set /p quality="Enter quality (64/128/192/256/320) [192]: "
if "%quality%"=="" set "quality=192"
echo.
echo Downloading with basic mode...
& "%python_exe%" youtube_to_mp3.py "%url%" -q "%quality%"
goto :end

:advanced_download
echo.
echo ⚡ Advanced Download Mode
set /p url="Enter YouTube URL or playlist URL: "
set /p quality="Enter quality (64/128/192/256/320) [192]: "
set /p workers="Enter number of parallel workers [3]: "
if "%quality%"=="" set "quality=192"
if "%workers%"=="" set "workers=3"
echo.
echo Downloading with advanced features (parallel, thumbnails, metadata)...
& "%python_exe%" youtube_to_mp3_advanced.py "%url%" -q "%quality%" -w "%workers%"
goto :end

:smart_download
echo.
echo 🧠 Smart Download Mode
set /p url="Enter YouTube URL or playlist URL: "
set /p quality="Enter quality (64/128/192/256/320) [192]: "
set /p workers="Enter number of parallel workers [3]: "
if "%quality%"=="" set "quality=192"
if "%workers%"=="" set "workers=3"
echo.
echo Downloading with smart features (duplicate detection, auto-retry, organization)...
& "%python_exe%" youtube_to_mp3_smart.py "%url%" -q "%quality%" -w "%workers%"
goto :end

:batch_download
echo.
echo 📋 Batch Download Mode
set /p file="Enter path to URLs file [urls_to_download.txt]: "
if "%file%"=="" set "file=urls_to_download.txt"
set /p quality="Enter quality (64/128/192/256/320) [192]: "
set /p workers="Enter number of parallel workers [3]: "
if "%quality%"=="" set "quality=192"
if "%workers%"=="" set "workers=3"

if not exist "%file%" (
    echo ❌ Error: File "%file%" not found.
    pause
    goto :show_menu
)

echo.
echo Select batch download mode:
echo 1. Basic batch download
echo 2. Advanced batch download (with thumbnails, resume)
echo 3. Smart batch download (with duplicate detection)
set /p batch_mode="Enter choice (1-3): "

if "%batch_mode%"=="1" (
    echo Downloading with basic batch mode...
    & "%python_exe%" youtube_to_mp3.py -f "%file%" -q "%quality%"
) else if "%batch_mode%"=="2" (
    echo Downloading with advanced batch mode...
    & "%python_exe%" youtube_to_mp3_advanced.py -f "%file%" -q "%quality%" -w "%workers%"
) else if "%batch_mode%"=="3" (
    echo Downloading with smart batch mode...
    & "%python_exe%" youtube_to_mp3_smart.py -f "%file%" -q "%quality%" -w "%workers%" --skip-duplicates
) else (
    echo Invalid choice. Using smart mode by default.
    & "%python_exe%" youtube_to_mp3_smart.py -f "%file%" -q "%quality%" -w "%workers%" --skip-duplicates
)
goto :end

:resume_download
echo.
echo 🔄 Resume Downloads Mode
echo Resuming failed downloads with smart features...
& "%python_exe%" youtube_to_mp3_smart.py --resume --max-retries 5
goto :end

:show_stats
echo.
echo 📊 Download Statistics
& "%python_exe%" youtube_to_mp3_smart.py --stats
pause
goto :show_menu

:install_ffmpeg
echo.
echo ⚙️ Installing FFmpeg...
call install_ffmpeg.bat
pause
goto :show_menu

:show_help
echo.
echo ❓ Detailed Usage Examples:
echo.
echo Command Line Usage:
echo   %~nx0 basic "https://youtube.com/watch?v=VIDEO_ID" 320
echo   %~nx0 advanced "https://youtube.com/watch?v=VIDEO_ID" 192 5
echo   %~nx0 smart "https://youtube.com/watch?v=VIDEO_ID" 256 3
echo   %~nx0 batch urls_to_download.txt 192 3
echo   %~nx0 resume
echo.
echo Quality Options: 64, 128, 192 (default), 256, 320 kbps
echo Workers: Number of parallel downloads (1-10, default: 3)
echo.
echo Features by Mode:
echo   Basic    : Simple downloads, basic metadata
echo   Advanced : Parallel downloads, thumbnails, resume, metadata
echo   Smart    : All advanced + duplicate detection, auto-retry, organization
echo.
pause
goto :show_menu

:execute_mode
if /i "%mode%"=="basic" (
    echo 🎵 Basic Download: %url_or_file%
    & "%python_exe%" youtube_to_mp3.py "%url_or_file%" -q "%quality%"
) else if /i "%mode%"=="advanced" (
    echo ⚡ Advanced Download: %url_or_file%
    & "%python_exe%" youtube_to_mp3_advanced.py "%url_or_file%" -q "%quality%" -w "%workers%"
) else if /i "%mode%"=="smart" (
    echo 🧠 Smart Download: %url_or_file%
    & "%python_exe%" youtube_to_mp3_smart.py "%url_or_file%" -q "%quality%" -w "%workers%"
) else if /i "%mode%"=="batch" (
    echo 📋 Smart Batch Download: %url_or_file%
    & "%python_exe%" youtube_to_mp3_smart.py -f "%url_or_file%" -q "%quality%" -w "%workers%" --skip-duplicates
) else if /i "%mode%"=="resume" (
    echo 🔄 Resuming Downloads...
    & "%python_exe%" youtube_to_mp3_smart.py --resume --max-retries 5
) else (
    goto :invalid_choice
)
goto :end

:invalid_choice
echo ❌ Invalid choice. Please try again.
pause
goto :show_menu

:exit
echo 👋 Goodbye!
exit /b 0

:end
echo.
echo ✅ Operation completed!
echo 📁 Check your downloads folder for the files.
echo.
pause
