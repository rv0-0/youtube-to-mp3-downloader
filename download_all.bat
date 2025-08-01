@echo off
echo YouTube to MP3 Batch Downloader
echo =================================
echo.

echo Starting batch download of all URLs...
echo This may take a while depending on video lengths and your internet speed.
echo.

"C:/Users/RAVI/Documents/Youtube Downloader/.venv/Scripts/python.exe" youtube_to_mp3.py -f urls_to_download.txt -o "Downloaded_Songs" -q 192

echo.
echo Batch download completed!
echo Check the "Downloaded_Songs" folder for your MP3 files.
echo.
pause
