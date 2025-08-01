#!/usr/bin/env python3
"""
Convert existing WebM files to MP3 using FFmpeg
"""

import os
import subprocess
from pathlib import Path

def convert_webm_to_mp3(input_folder="Downloaded_Songs", quality="192"):
    """
    Convert all .webm files in a folder to MP3 format.
    
    Args:
        input_folder (str): Folder containing .webm files
        quality (str): Audio quality in kbps
    """
    input_dir = Path(input_folder)
    ffmpeg_path = Path("ffmpeg/bin/ffmpeg.exe")
    
    if not ffmpeg_path.exists():
        print("❌ FFmpeg not found. Please install FFmpeg first.")
        return
    
    if not input_dir.exists():
        print(f"❌ Directory not found: {input_dir}")
        return
    
    webm_files = list(input_dir.glob("*.webm"))
    
    if not webm_files:
        print(f"❌ No .webm files found in {input_dir}")
        return
    
    print(f"🎵 Converting {len(webm_files)} WebM files to MP3")
    print(f"📁 Source directory: {input_dir.absolute()}")
    print(f"🎧 Audio quality: {quality} kbps")
    print("-" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, webm_file in enumerate(webm_files, 1):
        mp3_file = webm_file.with_suffix('.mp3')
        
        print(f"\n[{i}/{len(webm_files)}] Converting: {webm_file.name}")
        
        try:
            # FFmpeg command to convert webm to mp3
            cmd = [
                str(ffmpeg_path.absolute()),
                "-i", str(webm_file),
                "-vn",  # No video
                "-ar", "44100",  # Sample rate
                "-ac", "2",  # Stereo
                "-b:a", f"{quality}k",  # Bitrate
                "-f", "mp3",  # Output format
                str(mp3_file),
                "-y"  # Overwrite if exists
            ]
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Converted successfully")
                # Delete the original .webm file
                webm_file.unlink()
                success_count += 1
            else:
                print(f"❌ Conversion failed: {result.stderr}")
                failed_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"❌ Conversion timed out")
            failed_count += 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Conversion Summary:")
    print(f"✅ Successful conversions: {success_count}")
    print(f"❌ Failed conversions: {failed_count}")
    print(f"📁 MP3 files saved to: {input_dir.absolute()}")

if __name__ == "__main__":
    convert_webm_to_mp3()
