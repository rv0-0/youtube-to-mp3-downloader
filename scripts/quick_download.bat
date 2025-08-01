@echo off
echo.
echo ⚡ Quick Download - YouTube to MP3
echo.
set /p url="Paste YouTube URL: "
if "%url%"=="" (
    echo No URL provided. Exiting...
    pause
    exit /b 1
)

echo.
echo 🎵 Downloading with smart features (best quality, duplicate detection)...
cd /d "%~dp0.."
.\.venv\Scripts\python.exe src/youtube_to_mp3_smart.py "%url%" -q 320 -w 3
echo.
echo ✅ Download completed! Check your downloads folder.
pause
