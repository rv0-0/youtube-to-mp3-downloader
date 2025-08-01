@echo off
echo Advanced YouTube to MP3 Downloader
echo ==================================
echo.

set "python_exe=.\.venv\Scripts\python.exe"
set "script=youtube_to_mp3_advanced.py"

if "%~1"=="" (
    echo Usage Examples:
    echo.
    echo   Single video:
    echo   %0 "https://youtube.com/watch?v=VIDEO_ID"
    echo.
    echo   High quality with 5 parallel workers:
    echo   %0 "URL" 320 5
    echo.
    echo   Batch download from file:
    echo   %0 batch urls_to_download.txt
    echo.
    echo   Auto-detect playlist:
    echo   %0 playlist "VIDEO_URL_IN_PLAYLIST"
    echo.
    echo   Resume failed downloads:
    echo   %0 resume
    echo.
    pause
    exit /b 1
)

set "mode=%~1"
set "url=%~2"
set "quality=%~3"
set "workers=%~4"

if "%quality%"=="" set "quality=192"
if "%workers%"=="" set "workers=3"

echo Starting download with quality: %quality% kbps
echo Using %workers% parallel workers
echo.

if /i "%mode%"=="batch" (
    echo 📋 Batch download mode
    & "%python_exe%" "%script%" -f "%url%" -q "%quality%" -w "%workers%"
) else if /i "%mode%"=="playlist" (
    echo 📋 Playlist mode with auto-detection
    & "%python_exe%" "%script%" --auto-playlist "%url%" -q "%quality%" -w "%workers%"
) else if /i "%mode%"=="resume" (
    echo 🔄 Resume mode
    & "%python_exe%" "%script%" --resume -q "%quality%" -w "%workers%"
) else (
    echo 🎵 Single video mode
    & "%python_exe%" "%script%" "%mode%" -q "%quality%" -w "%workers%"
)

echo.
echo Download process completed!
pause
