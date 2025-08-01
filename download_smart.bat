@echo off
echo Smart YouTube to MP3 Downloader
echo ===============================
echo.

set "python_exe=.\.venv\Scripts\python.exe"
set "script=youtube_to_mp3_smart.py"

if "%~1"=="" (
    echo Smart Download Options:
    echo.
    echo   Single video with smart features:
    echo   %0 smart "https://youtube.com/watch?v=VIDEO_ID"
    echo.
    echo   Batch download with duplicate detection:
    echo   %0 batch urls_to_download.txt
    echo.
    echo   Resume failed downloads:
    echo   %0 resume
    echo.
    echo   Show statistics:
    echo   %0 stats
    echo.
    echo   High quality playlist with organization:
    echo   %0 playlist "PLAYLIST_URL" 320
    echo.
    echo   Auto-detect playlist from video:
    echo   %0 auto "VIDEO_URL_IN_PLAYLIST"
    echo.
    echo   Add to favorites:
    echo   %0 favorite VIDEO_ID
    echo.
    pause
    exit /b 1
)

set "mode=%~1"
set "url=%~2"
set "quality=%~3"

if "%quality%"=="" set "quality=192"

echo Smart YouTube to MP3 Downloader
echo Quality: %quality% kbps
echo Duplicate detection: Enabled
echo Auto-retry: Enabled
echo Playlist organization: Enabled
echo.

if /i "%mode%"=="smart" (
    echo 🧠 Smart single download mode
    & "%python_exe%" "%script%" "%url%" -q "%quality%" -w 2
) else if /i "%mode%"=="batch" (
    echo 🧠 Smart batch download mode
    & "%python_exe%" "%script%" -f "%url%" -q "%quality%" -w 3 --skip-duplicates
) else if /i "%mode%"=="resume" (
    echo 🔄 Resume failed downloads
    & "%python_exe%" "%script%" --resume -q "%quality%" -w 2 --max-retries 5
) else if /i "%mode%"=="stats" (
    echo 📊 Showing statistics
    & "%python_exe%" "%script%" --stats
) else if /i "%mode%"=="playlist" (
    echo 📋 Smart playlist mode
    & "%python_exe%" "%script%" -p "%url%" -q "%quality%" -w 3
) else if /i "%mode%"=="auto" (
    echo 🔍 Auto-detect playlist mode
    & "%python_exe%" "%script%" --auto-playlist "%url%" -q "%quality%" -w 3
) else if /i "%mode%"=="favorite" (
    echo ⭐ Adding to favorites
    & "%python_exe%" "%script%" --add-favorite "%url%"
) else (
    echo ❌ Unknown mode: %mode%
    echo Use without parameters to see available options.
    pause
    exit /b 1
)

echo.
echo Smart download process completed!
echo Check the downloads folder for your organized files.
pause
