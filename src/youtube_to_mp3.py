#!/usr/bin/env python3
"""
YouTube to MP3 Downloader
A simple script to download YouTube videos and convert them to MP3 format.
"""

import os
import sys
import argparse
from pathlib import Path
import yt_dlp


def download_youtube_to_mp3(url, output_path="downloads", quality="192"):
    """
    Download a YouTube video and convert it to MP3.
    
    Args:
        url (str): YouTube video URL
        output_path (str): Directory to save the MP3 file
        quality (str): Audio quality (64, 128, 192, 256, 320)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Check for local FFmpeg installation
        ffmpeg_path = None
        local_ffmpeg = Path("ffmpeg/bin/ffmpeg.exe")
        if local_ffmpeg.exists():
            ffmpeg_path = str(local_ffmpeg.absolute())
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'postprocessor_args': [
                '-ar', '44100',  # Set sample rate to 44.1kHz
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False,
        }
        
        # Add FFmpeg location if found locally
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        # Download and convert
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {url}")
            ydl.download([url])
            print("✅ Download completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error downloading video: {str(e)}")
        return False


def download_playlist_to_mp3(playlist_url, output_path="downloads", quality="192"):
    """
    Download all videos from a YouTube playlist and convert them to MP3.
    
    Args:
        playlist_url (str): YouTube playlist URL
        output_path (str): Directory to save the MP3 files
        quality (str): Audio quality (64, 128, 192, 256, 320)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options for playlist
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'postprocessor_args': [
                '-ar', '44100',  # Set sample rate to 44.1kHz
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'extract_flat': False,
        }
        
        # Download and convert playlist
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading playlist: {playlist_url}")
            ydl.download([playlist_url])
            print("✅ Playlist download completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error downloading playlist: {str(e)}")
        return False


def get_video_info(url):
    """
    Get information about a YouTube video without downloading it.
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        dict: Video information or None if error
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return None
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', 'Unknown'),
            }
    except Exception as e:
        print(f"❌ Error getting video info: {str(e)}")
        return None


def format_duration(seconds):
    """Convert seconds to MM:SS format."""
    if seconds:
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
    return "Unknown"


def batch_download_from_file(file_path, output_path="downloads", quality="192"):
    """
    Download multiple YouTube videos from a text file containing URLs.
    
    Args:
        file_path (str): Path to text file containing YouTube URLs (one per line)
        output_path (str): Directory to save the MP3 files
        quality (str): Audio quality (64, 128, 192, 256, 320)
    
    Returns:
        tuple: (success_count, failed_count, failed_urls)
    """
    try:
        # Read URLs from file
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("❌ No URLs found in the file")
            return 0, 0, []
        
        print(f"📋 Found {len(urls)} URLs to download")
        print(f"📁 Output directory: {Path(output_path).absolute()}")
        print(f"🎧 Audio quality: {quality} kbps")
        print("=" * 60)
        
        success_count = 0
        failed_count = 0
        failed_urls = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            # Skip duplicate URLs (remove duplicates but show progress)
            if url in [failed_url[1] for failed_url in failed_urls]:
                print("⏭️ Skipping duplicate URL")
                continue
                
            success = download_youtube_to_mp3(url, output_path, quality)
            
            if success:
                success_count += 1
                print(f"✅ Downloaded successfully ({success_count}/{len(urls)})")
            else:
                failed_count += 1
                failed_urls.append((i, url))
                print(f"❌ Failed to download ({failed_count} failures so far)")
            
            # Small delay between downloads to be respectful
            import time
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print(f"📊 Download Summary:")
        print(f"✅ Successful downloads: {success_count}")
        print(f"❌ Failed downloads: {failed_count}")
        print(f"📁 Files saved to: {Path(output_path).absolute()}")
        
        if failed_urls:
            print(f"\n❌ Failed URLs:")
            for idx, url in failed_urls:
                print(f"  [{idx}] {url}")
        
        return success_count, failed_count, failed_urls
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return 0, 0, []
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return 0, 0, []


def main():
    """Main function to handle command line arguments and execute downloads."""
    parser = argparse.ArgumentParser(
        description="Download YouTube videos as MP3 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -o music -q 320 https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -p https://www.youtube.com/playlist?list=PLexampleplaylist
  %(prog)s -i https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -f urls_to_download.txt
  %(prog)s -f urls_to_download.txt -o my_music -q 320
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',  # Make URL optional
        help='YouTube video or playlist URL'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='downloads',
        help='Output directory (default: downloads)'
    )
    
    parser.add_argument(
        '-q', '--quality',
        choices=['64', '128', '192', '256', '320'],
        default='192',
        help='Audio quality in kbps (default: 192)'
    )
    
    parser.add_argument(
        '-p', '--playlist',
        action='store_true',
        help='Download entire playlist'
    )
    
    parser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Show video information without downloading'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Download URLs from a text file (one URL per line)'
    )
    
    args = parser.parse_args()
    
    # Check if either URL or file is provided
    if not args.url and not args.file:
        print("❌ Please provide either a YouTube URL or a file containing URLs")
        parser.print_help()
        sys.exit(1)
    
    # Handle batch download from file
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        
        print(f"🎵 YouTube to MP3 Batch Downloader")
        success_count, failed_count, failed_urls = batch_download_from_file(
            args.file, args.output, args.quality
        )
        
        if success_count > 0:
            print(f"\n🎉 Successfully downloaded {success_count} videos!")
        if failed_count > 0:
            print(f"\n💔 {failed_count} downloads failed.")
        
        sys.exit(0 if failed_count == 0 else 1)
    
    # Validate URL for single downloads
    if not ('youtube.com' in args.url or 'youtu.be' in args.url):
        print("❌ Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Show video information only
    if args.info:
        print("📋 Getting video information...")
        info = get_video_info(args.url)
        if info:
            print(f"Title: {info['title']}")
            print(f"Duration: {format_duration(info['duration'])}")
            print(f"Uploader: {info['uploader']}")
            print(f"Views: {info['view_count']:,}")
            print(f"Upload Date: {info['upload_date']}")
        return
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(exist_ok=True)
    
    print(f"🎵 YouTube to MP3 Downloader")
    print(f"📁 Output directory: {output_path.absolute()}")
    print(f"🎧 Audio quality: {args.quality} kbps")
    print("-" * 50)
    
    # Download playlist or single video
    if args.playlist:
        success = download_playlist_to_mp3(args.url, args.output, args.quality)
    else:
        success = download_youtube_to_mp3(args.url, args.output, args.quality)
    
    if success:
        print(f"\n🎉 All downloads saved to: {output_path.absolute()}")
    else:
        print("\n💔 Download failed. Please check the URL and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
