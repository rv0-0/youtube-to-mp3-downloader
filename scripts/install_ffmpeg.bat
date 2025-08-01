@echo off
echo Installing FFmpeg for YouTube to MP3 Converter
echo ============================================
echo.

echo This script will download and install FFmpeg to enable MP3 conversion.
echo Please wait while we download FFmpeg...
echo.

:: Create ffmpeg directory
if not exist "ffmpeg" mkdir ffmpeg
cd ffmpeg

echo Downloading FFmpeg (this may take a few minutes)...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'}"

if exist "ffmpeg.zip" (
    echo Extracting FFmpeg...
    powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force}"
    
    :: Find the extracted folder and rename it
    for /d %%i in (ffmpeg-*) do (
        if exist "%%i\bin\ffmpeg.exe" (
            echo Moving FFmpeg files...
            xcopy "%%i\bin\*" "bin\" /Y /I
            rmdir "%%i" /S /Q
        )
    )
    
    del ffmpeg.zip
    
    if exist "bin\ffmpeg.exe" (
        echo.
        echo ✅ FFmpeg installed successfully!
        echo Location: %CD%\bin\
        echo.
        echo You can now run the YouTube downloader with MP3 conversion.
        echo.
    ) else (
        echo ❌ Installation failed. Please download FFmpeg manually from:
        echo https://ffmpeg.org/download.html#build-windows
    )
) else (
    echo ❌ Download failed. Please check your internet connection.
    echo You can manually download FFmpeg from:
    echo https://ffmpeg.org/download.html#build-windows
)

cd ..
echo.
pause
