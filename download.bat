@echo off
echo YouTube to MP3 Downloader
echo ========================
echo.

if "%~1"=="" (
    echo Usage: download.bat "https://youtube.com/watch?v=VIDEO_ID"
    echo.
    echo Examples:
    echo   download.bat "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    echo   download.bat "https://www.youtube.com/watch?v=dQw4w9WgXcQ" high_quality 320
    echo.
    pause
    exit /b 1
)

set "url=%~1"
set "output=%~2"
set "quality=%~3"

if "%output%"=="" set "output=downloads"
if "%quality%"=="" set "quality=192"

echo Downloading: %url%
echo Output folder: %output%
echo Quality: %quality% kbps
echo.

"C:/Users/RAVI/Documents/Youtube Downloader/.venv/Scripts/python.exe" youtube_to_mp3.py -o "%output%" -q "%quality%" "%url%"

echo.
pause
