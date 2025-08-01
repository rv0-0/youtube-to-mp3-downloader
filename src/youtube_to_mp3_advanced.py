#!/usr/bin/env python3
"""
Advanced YouTube to MP3 Downloader
Enhanced version with resume, thumbnails, metadata, parallel downloads, and more.
"""

import os
import sys
import json
import asyncio
import aiohttp
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs
import time
import hashlib
import threading
from typing import List, Dict, Optional, Tuple
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC, TIT2, TPE1, TALB, TDRC, TRCK
from PIL import Image
import requests


class AdvancedYouTubeDownloader:
    def __init__(self, output_path="downloads", quality="192", max_workers=3, rate_limit=None):
        self.output_path = Path(output_path)
        self.quality = quality
        self.max_workers = max_workers
        self.rate_limit = rate_limit  # KB/s
        self.download_history = {}
        self.failed_downloads = []
        self.success_count = 0
        self.total_count = 0
        self.lock = threading.Lock()
        
        # Create directories
        self.output_path.mkdir(exist_ok=True)
        self.thumbnails_path = self.output_path / "thumbnails"
        self.thumbnails_path.mkdir(exist_ok=True)
        self.metadata_path = self.output_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)
        
        # Load download history
        self.history_file = self.output_path / "download_history.json"
        self.load_download_history()
    
    def load_download_history(self):
        """Load download history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not load download history: {e}")
                self.download_history = {}
    
    def save_download_history(self):
        """Save download history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not save download history: {e}")
    
    def get_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        try:
            if 'youtu.be/' in url:
                return url.split('youtu.be/')[-1].split('?')[0]
            elif 'youtube.com/watch' in url:
                parsed = urlparse(url)
                return parse_qs(parsed.query)['v'][0]
            return hashlib.md5(url.encode()).hexdigest()[:11]
        except:
            return hashlib.md5(url.encode()).hexdigest()[:11]
    
    def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a playlist."""
        return 'playlist?' in url or 'list=' in url
    
    def detect_playlist_from_video(self, url: str) -> Optional[str]:
        """Detect if a single video URL is part of a playlist."""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            if 'list' in query_params:
                list_id = query_params['list'][0]
                if list_id and not list_id.startswith('WL'):  # Not Watch Later
                    return f"https://www.youtube.com/playlist?list={list_id}"
        except:
            pass
        return None
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """Get FFmpeg path."""
        local_ffmpeg = Path("ffmpeg/bin/ffmpeg.exe")
        if local_ffmpeg.exists():
            return str(local_ffmpeg.absolute())
        return None
    
    def extract_metadata(self, url: str) -> Dict:
        """Extract metadata from YouTube video."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    return {}
                
                metadata = {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'playlist_title': info.get('playlist_title', ''),
                    'playlist_index': info.get('playlist_index', 0),
                }
                
                return metadata
        except Exception as e:
            print(f"⚠️ Could not extract metadata: {e}")
            return {}
    
    async def download_thumbnail(self, thumbnail_url: str, video_id: str) -> Optional[Path]:
        """Download video thumbnail asynchronously."""
        if not thumbnail_url:
            return None
        
        try:
            thumbnail_path = self.thumbnails_path / f"{video_id}.jpg"
            
            if thumbnail_path.exists():
                return thumbnail_path
            
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save original thumbnail
                        with open(thumbnail_path, 'wb') as f:
                            f.write(content)
                        
                        # Convert to square album art
                        try:
                            with Image.open(thumbnail_path) as img:
                                # Create square thumbnail (500x500)
                                size = min(img.size)
                                img_crop = img.crop((
                                    (img.width - size) // 2,
                                    (img.height - size) // 2,
                                    (img.width + size) // 2,
                                    (img.height + size) // 2
                                ))
                                img_crop = img_crop.resize((500, 500), Image.Resampling.LANCZOS)
                                
                                # Save as album art
                                album_art_path = self.thumbnails_path / f"{video_id}_album.jpg"
                                img_crop.save(album_art_path, 'JPEG', quality=90)
                                
                                return album_art_path
                        except Exception as e:
                            print(f"⚠️ Could not process thumbnail: {e}")
                            return thumbnail_path
                        
                        return thumbnail_path
        except Exception as e:
            print(f"⚠️ Could not download thumbnail: {e}")
            return None
    
    def apply_metadata_to_mp3(self, mp3_path: Path, metadata: Dict, thumbnail_path: Optional[Path] = None):
        """Apply metadata and album art to MP3 file."""
        try:
            # Load MP3 file
            audio_file = MP3(mp3_path, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Ensure tags exist before proceeding
            if audio_file.tags is not None:
                # Clear existing tags
                audio_file.tags.clear()
                
                # Add metadata
                if metadata.get('title'):
                    audio_file.tags.add(TIT2(encoding=3, text=metadata['title']))
                
                if metadata.get('uploader'):
                    audio_file.tags.add(TPE1(encoding=3, text=metadata['uploader']))
                
                if metadata.get('playlist_title'):
                    audio_file.tags.add(TALB(encoding=3, text=metadata['playlist_title']))
                
                if metadata.get('upload_date'):
                    try:
                        year = metadata['upload_date'][:4]
                        audio_file.tags.add(TDRC(encoding=3, text=year))
                    except:
                        pass
                
                if metadata.get('playlist_index'):
                    audio_file.tags.add(TRCK(encoding=3, text=str(metadata['playlist_index'])))
                
                # Add album art
                if thumbnail_path and thumbnail_path.exists():
                    with open(thumbnail_path, 'rb') as f:
                        album_art = f.read()
                    
                    audio_file.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=album_art
                        )
                    )
            
            # Save changes
            audio_file.save()
            
            print("🎵 Applied metadata and album art")
            
        except Exception as e:
            print(f"⚠️ Could not apply metadata: {e}")
    
    def save_metadata_file(self, metadata: Dict, video_id: str):
        """Save metadata to JSON file."""
        try:
            metadata_file = self.metadata_path / f"{video_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save metadata file: {e}")
    
    def check_resume(self, video_id: str, expected_title: Optional[str] = None) -> Optional[Path]:
        """Check if download can be resumed or if file already exists."""
        # Check if already downloaded successfully
        if video_id in self.download_history:
            history_entry = self.download_history[video_id]
            if history_entry.get('status') == 'completed':
                file_path = Path(history_entry.get('file_path', ''))
                if file_path.exists():
                    print(f"✅ Already downloaded: {file_path.name}")
                    return file_path
        
        # Check for partial downloads (webm files)
        for ext in ['.webm', '.m4a', '.mp4']:
            pattern = f"*{video_id}*{ext}"
            matches = list(self.output_path.glob(pattern))
            if matches:
                print(f"🔄 Found partial download, will resume: {matches[0].name}")
                return None  # Will resume
        
        # Check for existing MP3 files
        if expected_title:
            clean_title = "".join(c for c in expected_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            mp3_pattern = f"*{clean_title}*.mp3"
            matches = list(self.output_path.glob(mp3_pattern))
            if matches:
                print(f"✅ Similar file exists: {matches[0].name}")
                return matches[0]
        
        return None
    
    def download_single_video(self, url: str, thread_id: int = 0) -> Tuple[bool, str, Optional[Path]]:
        """Download a single video with all advanced features."""
        try:
            print(f"\n[Thread {thread_id}] 🎵 Processing: {url}")
            
            # Extract metadata first
            print(f"[Thread {thread_id}] 📋 Extracting metadata...")
            metadata = self.extract_metadata(url)
            
            if not metadata:
                return False, "Could not extract metadata", None
            
            video_id = metadata.get('id', self.get_video_id(url))
            title = metadata.get('title', 'Unknown')
            
            print(f"[Thread {thread_id}] 📺 Title: {title}")
            print(f"[Thread {thread_id}] 👤 Uploader: {metadata.get('uploader', 'Unknown')}")
            print(f"[Thread {thread_id}] ⏱️ Duration: {self.format_duration(metadata.get('duration', 0))}")
            
            # Check for resume/existing files
            existing_file = self.check_resume(video_id, title)
            if existing_file:
                with self.lock:
                    self.success_count += 1
                return True, "Already exists", existing_file
            
            # Save metadata
            self.save_metadata_file(metadata, video_id)
            
            # Download thumbnail
            thumbnail_path = None
            if metadata.get('thumbnail'):
                print(f"[Thread {thread_id}] 🖼️ Downloading thumbnail...")
                thumbnail_path = asyncio.run(self.download_thumbnail(metadata['thumbnail'], video_id))
            
            # Configure yt-dlp options
            ffmpeg_path = self.get_ffmpeg_path()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
                'postprocessor_args': [
                    '-ar', '44100',
                ],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'writethumbnail': False,  # We handle thumbnails manually
                'writeinfojson': False,   # We handle metadata manually
            }
            
            # Add FFmpeg location if available
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            # Add rate limiting if specified
            if self.rate_limit:
                ydl_opts['ratelimit'] = self.rate_limit * 1024  # Convert KB/s to B/s
            
            # Download and convert
            print(f"[Thread {thread_id}] ⬇️ Downloading and converting...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded MP3 file
            mp3_files = list(self.output_path.glob("*.mp3"))
            mp3_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)  # Get newest
            
            if mp3_files:
                mp3_path = mp3_files[0]
                
                # Apply metadata and album art
                print(f"[Thread {thread_id}] 🏷️ Applying metadata and album art...")
                self.apply_metadata_to_mp3(mp3_path, metadata, thumbnail_path)
                
                # Update download history
                with self.lock:
                    self.download_history[video_id] = {
                        'url': url,
                        'title': title,
                        'file_path': str(mp3_path),
                        'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'completed',
                        'metadata': metadata
                    }
                    self.success_count += 1
                
                print(f"[Thread {thread_id}] ✅ Download completed: {mp3_path.name}")
                return True, "Success", mp3_path
            else:
                return False, "MP3 file not found after conversion", None
            
        except Exception as e:
            error_msg = f"Error downloading video: {str(e)}"
            print(f"[Thread {thread_id}] ❌ {error_msg}")
            
            with self.lock:
                self.failed_downloads.append({
                    'url': url,
                    'error': error_msg,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return False, error_msg, None
    
    def format_duration(self, seconds):
        """Convert seconds to HH:MM:SS format."""
        if not seconds:
            return "Unknown"
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def download_parallel(self, urls: List[str]) -> Dict:
        """Download multiple URLs in parallel."""
        self.total_count = len(urls)
        print(f"\n🚀 Starting parallel download of {self.total_count} videos")
        print(f"⚡ Using {self.max_workers} parallel workers")
        if self.rate_limit:
            print(f"🐌 Rate limit: {self.rate_limit} KB/s per download")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_url = {
                executor.submit(self.download_single_video, url, i % self.max_workers): url 
                for i, url in enumerate(urls)
            }
            
            # Process completed downloads
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success, message, file_path = future.result()
                    
                    with self.lock:
                        progress = f"[{self.success_count + len(self.failed_downloads)}/{self.total_count}]"
                        if success:
                            print(f"\n{progress} ✅ Success: {message}")
                        else:
                            print(f"\n{progress} ❌ Failed: {message}")
                            
                except Exception as e:
                    print(f"\n❌ Unexpected error for {url}: {e}")
                    with self.lock:
                        self.failed_downloads.append({
                            'url': url,
                            'error': str(e),
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        
        # Save download history
        self.save_download_history()
        
        # Calculate statistics
        end_time = time.time()
        total_time = end_time - start_time
        failed_count = len(self.failed_downloads)
        
        return {
            'success_count': self.success_count,
            'failed_count': failed_count,
            'total_count': self.total_count,
            'total_time': total_time,
            'failed_downloads': self.failed_downloads
        }
    
    def get_playlist_urls(self, playlist_url: str) -> List[str]:
        """Extract all video URLs from a playlist."""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_json': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if playlist_info is None:
                    print("❌ Could not extract playlist information")
                    return []
                
                if 'entries' in playlist_info and playlist_info['entries']:
                    urls = []
                    for entry in playlist_info['entries']:
                        if entry and entry.get('url'):
                            urls.append(entry['url'])
                        elif entry and entry.get('id'):
                            urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                    
                    title = playlist_info.get('title', 'Unknown') if playlist_info else 'Unknown'
                    print(f"📋 Found {len(urls)} videos in playlist: {title}")
                    return urls
                else:
                    print("❌ No videos found in playlist")
                    return []
                    
        except Exception as e:
            print(f"❌ Error extracting playlist: {e}")
            return []


def main():
    """Main function with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="Advanced YouTube to MP3 Downloader with resume, thumbnails, metadata, and parallel downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Advanced Features:
  • Resume interrupted downloads automatically
  • Download and embed thumbnails as album art
  • Extract and apply metadata (title, artist, duration, etc.)
  • Automatic playlist detection from video URLs
  • Parallel downloads for faster processing
  • Rate limiting to be respectful to servers
  • Download history tracking

Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -o music -q 320 -w 5 https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -f urls.txt -w 3 --rate-limit 500
  %(prog)s -p https://www.youtube.com/playlist?list=PLexample
  %(prog)s --auto-playlist https://www.youtube.com/watch?v=dQw4w9WgXcQ
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
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
        '-f', '--file',
        help='Download URLs from a text file (one URL per line)'
    )
    
    parser.add_argument(
        '-p', '--playlist',
        action='store_true',
        help='Download entire playlist'
    )
    
    parser.add_argument(
        '--auto-playlist',
        action='store_true',
        help='Automatically detect and download entire playlist from video URL'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=3,
        help='Number of parallel download workers (default: 3)'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=int,
        help='Rate limit in KB/s per download (e.g., 500 for 500 KB/s)'
    )
    
    parser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Show video information without downloading'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume previous failed downloads'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.url and not args.file and not args.resume:
        print("❌ Please provide either a YouTube URL, a file containing URLs, or use --resume")
        parser.print_help()
        sys.exit(1)
    
    # Create downloader instance
    downloader = AdvancedYouTubeDownloader(
        output_path=args.output,
        quality=args.quality,
        max_workers=args.workers,
        rate_limit=args.rate_limit
    )
    
    print(f"🎵 Advanced YouTube to MP3 Downloader")
    print(f"📁 Output directory: {downloader.output_path.absolute()}")
    print(f"🎧 Audio quality: {args.quality} kbps")
    print(f"⚡ Parallel workers: {args.workers}")
    if args.rate_limit:
        print(f"🐌 Rate limit: {args.rate_limit} KB/s per download")
    
    urls_to_download = []
    
    # Resume previous downloads
    if args.resume:
        print("\n🔄 Resuming previous failed downloads...")
        failed_downloads = downloader.failed_downloads
        if failed_downloads:
            urls_to_download = [item['url'] for item in failed_downloads]
            print(f"📋 Found {len(urls_to_download)} failed downloads to retry")
        else:
            print("✅ No failed downloads to resume")
            return
    
    # Handle file input
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                urls_to_download = [line.strip() for line in f if line.strip()]
            print(f"📋 Loaded {len(urls_to_download)} URLs from file")
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    
    # Handle single URL
    elif args.url:
        # Check for info mode
        if args.info:
            print("\n📋 Getting video information...")
            metadata = downloader.extract_metadata(args.url)
            if metadata:
                print(f"📺 Title: {metadata.get('title', 'Unknown')}")
                print(f"👤 Uploader: {metadata.get('uploader', 'Unknown')}")
                print(f"⏱️ Duration: {downloader.format_duration(metadata.get('duration', 0))}")
                print(f"👀 Views: {metadata.get('view_count', 0):,}")
                print(f"📅 Upload Date: {metadata.get('upload_date', 'Unknown')}")
                if metadata.get('description'):
                    print(f"📝 Description: {metadata['description'][:200]}...")
            return
        
        # Auto-detect playlist
        if args.auto_playlist:
            playlist_url = downloader.detect_playlist_from_video(args.url)
            if playlist_url:
                print(f"🔍 Detected playlist: {playlist_url}")
                urls_to_download = downloader.get_playlist_urls(playlist_url)
            else:
                print("ℹ️ No playlist detected, downloading single video")
                urls_to_download = [args.url]
        
        # Handle playlist
        elif args.playlist or downloader.is_playlist_url(args.url):
            urls_to_download = downloader.get_playlist_urls(args.url)
        
        # Single video
        else:
            urls_to_download = [args.url]
    
    if not urls_to_download:
        print("❌ No URLs to download")
        sys.exit(1)
    
    # Start downloads
    print("\n" + "=" * 60)
    start_time = time.time()
    
    if len(urls_to_download) == 1:
        # Single download
        success, message, file_path = downloader.download_single_video(urls_to_download[0])
        if success:
            print(f"\n🎉 Download completed: {file_path}")
        else:
            print(f"\n💔 Download failed: {message}")
            sys.exit(1)
    else:
        # Parallel downloads
        results = downloader.download_parallel(urls_to_download)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Download Summary:")
        print(f"✅ Successful downloads: {results['success_count']}")
        print(f"❌ Failed downloads: {results['failed_count']}")
        print(f"📁 Files saved to: {downloader.output_path.absolute()}")
        print(f"⏱️ Total time: {results['total_time']:.1f} seconds")
        
        if results['failed_downloads']:
            print(f"\n❌ Failed URLs:")
            for item in results['failed_downloads']:
                print(f"  • {item['url']} - {item['error']}")
            print(f"\n💡 Use --resume to retry failed downloads")
        
        if results['failed_count'] > 0:
            sys.exit(1)
    
    print(f"\n🎉 All downloads completed successfully!")


if __name__ == "__main__":
    main()
