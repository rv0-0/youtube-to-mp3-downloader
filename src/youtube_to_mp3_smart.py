#!/usr/bin/env python3
"""
Smart YouTube to MP3 Downloader
Enhanced version with duplicate detection, auto-retry, playlist organization, favorites, and more.
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
from typing import List, Dict, Optional, Tuple, Set
import random
import math
from filelock import FileLock
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC, TIT2, TPE1, TALB, TDRC, TRCK, TPOS, TCON
from PIL import Image
import requests


class SmartYouTubeDownloader:
    def __init__(self, output_path="downloads", quality="192", max_workers=3, rate_limit=None, organize_playlists=True):
        self.output_path = Path(output_path)
        self.quality = quality
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.organize_playlists = organize_playlists
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.download_history = {}
        self.favorites = set()
        self.duplicates_found = []
        self.failed_downloads = []
        self.success_count = 0
        self.total_count = 0
        self.skipped_count = 0
        
        # Create directory structure
        self.setup_directories()
        
        # Load persistent data
        self.load_download_history()
        self.load_favorites()
        
        # Duplicate detection cache
        self.content_hashes = {}
        self.title_similarity_cache = {}
    
    def setup_directories(self):
        """Create organized directory structure."""
        self.output_path.mkdir(exist_ok=True)
        
        # Core directories
        self.thumbnails_path = self.output_path / "thumbnails"
        self.metadata_path = self.output_path / "metadata"
        self.playlists_path = self.output_path / "playlists"
        self.history_path = self.output_path / ".history"
        
        # Create directories
        for path in [self.thumbnails_path, self.metadata_path, self.playlists_path, self.history_path]:
            path.mkdir(exist_ok=True)
        
        # Data files
        self.history_file = self.history_path / "download_history.json"
        self.favorites_file = self.history_path / "favorites.json"
        self.duplicates_file = self.history_path / "duplicates.json"
        self.stats_file = self.history_path / "statistics.json"
    
    def load_download_history(self):
        """Load download history with file locking."""
        lock_file = str(self.history_file) + ".lock"
        with FileLock(lock_file):
            if self.history_file.exists():
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.download_history = data.get('downloads', {})
                        self.content_hashes = data.get('content_hashes', {})
                except Exception as e:
                    print(f"⚠️ Warning: Could not load download history: {e}")
                    self.download_history = {}
                    self.content_hashes = {}
    
    def save_download_history(self):
        """Save download history with file locking."""
        lock_file = str(self.history_file) + ".lock"
        with FileLock(lock_file):
            try:
                data = {
                    'downloads': self.download_history,
                    'content_hashes': self.content_hashes,
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Warning: Could not save download history: {e}")
    
    def load_favorites(self):
        """Load favorites list."""
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = set(json.load(f))
            except Exception as e:
                print(f"⚠️ Warning: Could not load favorites: {e}")
                self.favorites = set()
    
    def save_favorites(self):
        """Save favorites list."""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.favorites), f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save favorites: {e}")
    
    def save_statistics(self):
        """Save download statistics."""
        try:
            stats = {
                'total_downloads': len(self.download_history),
                'successful_downloads': self.success_count,
                'failed_downloads': len(self.failed_downloads),
                'duplicates_detected': len(self.duplicates_found),
                'favorites_count': len(self.favorites),
                'last_session': {
                    'success_count': self.success_count,
                    'failed_count': len(self.failed_downloads),
                    'skipped_count': self.skipped_count,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save statistics: {e}")
    
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
    
    def calculate_content_hash(self, title: str, duration: int, uploader: str) -> str:
        """Calculate a content hash for duplicate detection."""
        # Normalize title for better duplicate detection
        normalized_title = ''.join(c.lower() for c in title if c.isalnum())
        content_string = f"{normalized_title}_{duration}_{uploader.lower()}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def similarity_score(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        # Simple word-based similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def detect_duplicate(self, metadata: Dict) -> Optional[Dict]:
        """Detect if this content is a duplicate of existing downloads."""
        title = metadata.get('title', '')
        duration = metadata.get('duration', 0)
        uploader = metadata.get('uploader', '')
        video_id = metadata.get('id', '')
        
        # Check exact video ID match
        if video_id in self.download_history:
            existing = self.download_history[video_id]
            if existing.get('status') == 'completed':
                return {
                    'type': 'exact_id',
                    'existing_entry': existing,
                    'reason': 'Same video ID already downloaded'
                }
        
        # Calculate content hash
        content_hash = self.calculate_content_hash(title, duration, uploader)
        
        # Check content hash match
        if content_hash in self.content_hashes:
            existing_id = self.content_hashes[content_hash]
            if existing_id in self.download_history:
                existing = self.download_history[existing_id]
                if existing.get('status') == 'completed':
                    return {
                        'type': 'content_hash',
                        'existing_entry': existing,
                        'reason': 'Similar content already downloaded (same title, duration, uploader)'
                    }
        
        # Check title similarity with duration tolerance
        for existing_id, existing_data in self.download_history.items():
            if existing_data.get('status') != 'completed':
                continue
            
            existing_metadata = existing_data.get('metadata', {})
            existing_title = existing_metadata.get('title', '')
            existing_duration = existing_metadata.get('duration', 0)
            existing_uploader = existing_metadata.get('uploader', '')
            
            # Skip if same uploader (likely different versions)
            if uploader.lower() == existing_uploader.lower():
                continue
            
            # Check title similarity
            similarity = self.similarity_score(title, existing_title)
            duration_diff = abs(duration - existing_duration) if duration and existing_duration else float('inf')
            
            # High similarity + similar duration = likely duplicate
            if similarity > 0.8 and duration_diff < 30:  # 30 seconds tolerance
                return {
                    'type': 'similar_content',
                    'existing_entry': existing_data,
                    'reason': f'Very similar content found (similarity: {similarity:.2f}, duration diff: {duration_diff}s)',
                    'similarity_score': similarity
                }
        
        return None
    
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
                if list_id and not list_id.startswith('WL'):
                    return f"https://www.youtube.com/playlist?list={list_id}"
        except:
            pass
        return None
    
    def get_playlist_output_path(self, playlist_title: str) -> Path:
        """Get organized output path for playlist."""
        if not self.organize_playlists or not playlist_title:
            return self.output_path
        
        # Clean playlist title for folder name
        clean_title = "".join(c for c in playlist_title if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_title = clean_title[:100]  # Limit length
        
        playlist_folder = self.playlists_path / clean_title
        playlist_folder.mkdir(exist_ok=True)
        
        return playlist_folder
    
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
                    'playlist_id': info.get('playlist_id', ''),
                    'categories': info.get('categories', []),
                    'like_count': info.get('like_count', 0),
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
                        
                        with open(thumbnail_path, 'wb') as f:
                            f.write(content)
                        
                        # Create album art
                        try:
                            with Image.open(thumbnail_path) as img:
                                size = min(img.size)
                                img_crop = img.crop((
                                    (img.width - size) // 2,
                                    (img.height - size) // 2,
                                    (img.width + size) // 2,
                                    (img.height + size) // 2
                                ))
                                img_crop = img_crop.resize((500, 500), Image.Resampling.LANCZOS)
                                
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
    
    def apply_enhanced_metadata(self, mp3_path: Path, metadata: Dict, thumbnail_path: Optional[Path] = None):
        """Apply enhanced metadata and tags to MP3 file."""
        try:
            audio_file = MP3(mp3_path, ID3=ID3)
            
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Ensure tags exist before proceeding
            if audio_file.tags is not None:
                audio_file.tags.clear()
                
                # Basic metadata
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
                
                # Enhanced metadata
                if metadata.get('categories'):
                    # Use first category as genre
                    genre = metadata['categories'][0] if metadata['categories'] else 'Music'
                    audio_file.tags.add(TCON(encoding=3, text=genre))
                
                if metadata.get('playlist_id'):
                    # Store playlist info
                    audio_file.tags.add(TPOS(encoding=3, text=f"Playlist: {metadata['playlist_id']}"))
                
                # Album art
                if thumbnail_path and thumbnail_path.exists():
                    with open(thumbnail_path, 'rb') as f:
                        album_art = f.read()
                    
                    audio_file.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=album_art
                        )
                    )
            
            audio_file.save()
            print("🎵 Applied enhanced metadata and album art")
            
        except Exception as e:
            print(f"⚠️ Could not apply metadata: {e}")
    
    def save_metadata_file(self, metadata: Dict, video_id: str):
        """Save detailed metadata to JSON file."""
        try:
            metadata_file = self.metadata_path / f"{video_id}.json"
            enhanced_metadata = metadata.copy()
            enhanced_metadata['download_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            enhanced_metadata['content_hash'] = self.calculate_content_hash(
                metadata.get('title', ''),
                metadata.get('duration', 0),
                metadata.get('uploader', '')
            )
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save metadata file: {e}")
    
    def retry_with_exponential_backoff(self, func, max_retries=3, base_delay=1, max_delay=60, *args, **kwargs):
        """Retry function with exponential backoff."""
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                # Calculate delay with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, 0.1) * delay
                total_delay = delay + jitter
                
                print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                print(f"🔄 Retrying in {total_delay:.1f} seconds...")
                time.sleep(total_delay)
    
    def download_single_video(self, url: str, thread_id: int = 0, max_retries: int = 3) -> Tuple[bool, str, Optional[Path]]:
        """Download a single video with smart features and auto-retry."""
        try:
            print(f"\n[Thread {thread_id}] 🎵 Processing: {url}")
            
            # Extract metadata with retry
            print(f"[Thread {thread_id}] 📋 Extracting metadata...")
            metadata = self.retry_with_exponential_backoff(
                self.extract_metadata, max_retries, 2, 30, url
            )
            
            if not metadata:
                return False, "Could not extract metadata after retries", None
            
            video_id = metadata.get('id', self.get_video_id(url))
            title = metadata.get('title', 'Unknown')
            
            print(f"[Thread {thread_id}] 📺 Title: {title}")
            print(f"[Thread {thread_id}] 👤 Uploader: {metadata.get('uploader', 'Unknown')}")
            print(f"[Thread {thread_id}] ⏱️ Duration: {self.format_duration(metadata.get('duration', 0))}")
            
            # Duplicate detection
            duplicate_info = self.detect_duplicate(metadata)
            if duplicate_info:
                print(f"[Thread {thread_id}] 🔍 Duplicate detected: {duplicate_info['reason']}")
                
                with self.lock:
                    self.duplicates_found.append({
                        'url': url,
                        'video_id': video_id,
                        'title': title,
                        'duplicate_info': duplicate_info,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    self.skipped_count += 1
                
                existing_file = Path(duplicate_info['existing_entry'].get('file_path', ''))
                if existing_file.exists():
                    print(f"[Thread {thread_id}] ✅ Using existing file: {existing_file.name}")
                    return True, "Duplicate skipped", existing_file
                else:
                    print(f"[Thread {thread_id}] ⚠️ Existing file not found, downloading anyway")
            
            # Determine output path (playlist organization)
            playlist_title = metadata.get('playlist_title', '')
            output_dir = self.get_playlist_output_path(playlist_title)
            
            if playlist_title and output_dir != self.output_path:
                print(f"[Thread {thread_id}] 📁 Organizing into playlist folder: {output_dir.name}")
            
            # Save metadata
            self.save_metadata_file(metadata, video_id)
            
            # Download thumbnail
            thumbnail_path = None
            if metadata.get('thumbnail'):
                print(f"[Thread {thread_id}] 🖼️ Downloading thumbnail...")
                thumbnail_path = asyncio.run(self.download_thumbnail(metadata['thumbnail'], video_id))
            
            # Configure yt-dlp
            ffmpeg_path = self.get_ffmpeg_path()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
                'postprocessor_args': ['-ar', '44100'],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'writethumbnail': False,
                'writeinfojson': False,
            }
            
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            if self.rate_limit:
                ydl_opts['ratelimit'] = self.rate_limit * 1024
            
            # Download with retry
            print(f"[Thread {thread_id}] ⬇️ Downloading and converting...")
            
            def download_func():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            
            self.retry_with_exponential_backoff(download_func, max_retries, 3, 60)
            
            # Find downloaded file
            mp3_files = list(output_dir.glob("*.mp3"))
            mp3_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if mp3_files:
                mp3_path = mp3_files[0]
                
                # Apply enhanced metadata
                print(f"[Thread {thread_id}] 🏷️ Applying enhanced metadata...")
                self.apply_enhanced_metadata(mp3_path, metadata, thumbnail_path)
                
                # Update records
                content_hash = self.calculate_content_hash(
                    metadata.get('title', ''),
                    metadata.get('duration', 0),
                    metadata.get('uploader', '')
                )
                
                with self.lock:
                    self.download_history[video_id] = {
                        'url': url,
                        'title': title,
                        'file_path': str(mp3_path),
                        'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'completed',
                        'metadata': metadata,
                        'content_hash': content_hash,
                        'playlist_organized': output_dir != self.output_path
                    }
                    self.content_hashes[content_hash] = video_id
                    self.success_count += 1
                
                print(f"[Thread {thread_id}] ✅ Download completed: {mp3_path.name}")
                return True, "Success", mp3_path
            else:
                return False, "MP3 file not found after conversion", None
            
        except Exception as e:
            error_msg = f"Error downloading video after {max_retries} retries: {str(e)}"
            print(f"[Thread {thread_id}] ❌ {error_msg}")
            
            with self.lock:
                self.failed_downloads.append({
                    'url': url,
                    'error': error_msg,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'retries_attempted': max_retries
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
    
    def add_to_favorites(self, video_id: str, title: str):
        """Add a video to favorites."""
        with self.lock:
            self.favorites.add(video_id)
            print(f"⭐ Added to favorites: {title}")
    
    def download_parallel(self, urls: List[str], auto_retry: bool = True) -> Dict:
        """Download multiple URLs in parallel with smart features."""
        self.total_count = len(urls)
        print(f"\n🚀 Starting smart parallel download of {self.total_count} videos")
        print(f"⚡ Using {self.max_workers} parallel workers")
        print(f"🧠 Smart features: duplicate detection, auto-retry, playlist organization")
        if self.rate_limit:
            print(f"🐌 Rate limit: {self.rate_limit} KB/s per download")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.download_single_video, url, i % self.max_workers): url 
                for i, url in enumerate(urls)
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success, message, file_path = future.result()
                    
                    with self.lock:
                        completed = self.success_count + len(self.failed_downloads) + self.skipped_count
                        progress = f"[{completed}/{self.total_count}]"
                        
                        if success:
                            if "skipped" in message.lower():
                                print(f"\n{progress} ⏭️ Skipped: {message}")
                            else:
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
        
        # Save all data
        self.save_download_history()
        self.save_favorites()
        self.save_statistics()
        
        # Save duplicates report
        if self.duplicates_found:
            try:
                with open(self.duplicates_file, 'w', encoding='utf-8') as f:
                    json.dump(self.duplicates_found, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Could not save duplicates report: {e}")
        
        # Calculate statistics
        end_time = time.time()
        total_time = end_time - start_time
        failed_count = len(self.failed_downloads)
        
        return {
            'success_count': self.success_count,
            'failed_count': failed_count,
            'skipped_count': self.skipped_count,
            'duplicates_count': len(self.duplicates_found),
            'total_count': self.total_count,
            'total_time': total_time,
            'failed_downloads': self.failed_downloads,
            'duplicates_found': self.duplicates_found
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
    
    def show_statistics(self):
        """Display download statistics."""
        print("\n📊 Download Statistics:")
        print(f"📁 Total downloads: {len(self.download_history)}")
        print(f"⭐ Favorites: {len(self.favorites)}")
        print(f"🔍 Duplicates detected: {len(self.duplicates_found)}")
        
        if self.duplicates_found:
            print("\n🔍 Recent duplicates:")
            for dup in self.duplicates_found[-5:]:  # Show last 5
                print(f"  • {dup['title']} - {dup['duplicate_info']['reason']}")
        
        # Show playlist organization
        playlist_folders = [d for d in self.playlists_path.iterdir() if d.is_dir()]
        if playlist_folders:
            print(f"\n📁 Organized playlists: {len(playlist_folders)}")
            for folder in playlist_folders[:5]:  # Show first 5
                mp3_count = len(list(folder.glob("*.mp3")))
                print(f"  • {folder.name} ({mp3_count} songs)")


def main():
    """Main function with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="Smart YouTube to MP3 Downloader with duplicate detection, auto-retry, and playlist organization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Smart Features:
  • Intelligent duplicate detection and skipping
  • Automatic metadata tagging with enhanced info
  • Playlist organization into separate folders
  • Download history and favorites tracking
  • Auto-retry with exponential backoff
  • Content-based duplicate detection
  • Smart file organization

Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -f urls.txt -w 3 --no-organize
  %(prog)s --auto-playlist https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s --resume --max-retries 5
  %(prog)s --stats
  %(prog)s --add-favorite VIDEO_ID
        """
    )
    
    # Main arguments
    parser.add_argument('url', nargs='?', help='YouTube video or playlist URL')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory (default: downloads)')
    parser.add_argument('-q', '--quality', choices=['64', '128', '192', '256', '320'], default='192', help='Audio quality in kbps (default: 192)')
    parser.add_argument('-f', '--file', help='Download URLs from a text file (one URL per line)')
    parser.add_argument('-p', '--playlist', action='store_true', help='Download entire playlist')
    parser.add_argument('--auto-playlist', action='store_true', help='Automatically detect and download entire playlist from video URL')
    parser.add_argument('-w', '--workers', type=int, default=3, help='Number of parallel download workers (default: 3)')
    parser.add_argument('--rate-limit', type=int, help='Rate limit in KB/s per download')
    parser.add_argument('-i', '--info', action='store_true', help='Show video information without downloading')
    
    # Smart features
    parser.add_argument('--resume', action='store_true', help='Resume previous failed downloads')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum retries for failed downloads (default: 3)')
    parser.add_argument('--no-organize', action='store_true', help='Disable playlist organization into folders')
    parser.add_argument('--stats', action='store_true', help='Show download statistics')
    parser.add_argument('--add-favorite', help='Add a video ID to favorites')
    parser.add_argument('--skip-duplicates', action='store_true', help='Enable duplicate detection and skipping')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.stats:
        downloader = SmartYouTubeDownloader(output_path=args.output)
        downloader.show_statistics()
        return
    
    if args.add_favorite:
        downloader = SmartYouTubeDownloader(output_path=args.output)
        downloader.add_to_favorites(args.add_favorite, "Manual addition")
        downloader.save_favorites()
        print(f"⭐ Added {args.add_favorite} to favorites")
        return
    
    # Validate input
    if not args.url and not args.file and not args.resume:
        print("❌ Please provide either a YouTube URL, a file containing URLs, or use --resume")
        parser.print_help()
        sys.exit(1)
    
    # Create smart downloader instance
    downloader = SmartYouTubeDownloader(
        output_path=args.output,
        quality=args.quality,
        max_workers=args.workers,
        rate_limit=args.rate_limit,
        organize_playlists=not args.no_organize
    )
    
    print(f"🧠 Smart YouTube to MP3 Downloader")
    print(f"📁 Output directory: {downloader.output_path.absolute()}")
    print(f"🎧 Audio quality: {args.quality} kbps")
    print(f"⚡ Parallel workers: {args.workers}")
    print(f"📁 Playlist organization: {'Enabled' if not args.no_organize else 'Disabled'}")
    print(f"🔍 Duplicate detection: Enabled")
    print(f"🔄 Auto-retry: {args.max_retries} attempts")
    if args.rate_limit:
        print(f"🐌 Rate limit: {args.rate_limit} KB/s per download")
    
    urls_to_download = []
    
    # Resume previous downloads
    if args.resume:
        print("\n🔄 Resuming previous failed downloads...")
        if downloader.failed_downloads:
            urls_to_download = [item['url'] for item in downloader.failed_downloads]
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
        if args.info:
            print("\n📋 Getting video information...")
            metadata = downloader.extract_metadata(args.url)
            if metadata:
                print(f"📺 Title: {metadata.get('title', 'Unknown')}")
                print(f"👤 Uploader: {metadata.get('uploader', 'Unknown')}")
                print(f"⏱️ Duration: {downloader.format_duration(metadata.get('duration', 0))}")
                print(f"👀 Views: {metadata.get('view_count', 0):,}")
                print(f"📅 Upload Date: {metadata.get('upload_date', 'Unknown')}")
                print(f"🏷️ Tags: {', '.join(metadata.get('tags', [])[:5])}")
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
    
    if len(urls_to_download) == 1:
        # Single download
        success, message, file_path = downloader.download_single_video(urls_to_download[0], max_retries=args.max_retries)
        if success:
            print(f"\n🎉 Download completed: {file_path}")
        else:
            print(f"\n💔 Download failed: {message}")
            sys.exit(1)
    else:
        # Smart parallel downloads
        results = downloader.download_parallel(urls_to_download)
        
        # Print comprehensive summary
        print("\n" + "=" * 60)
        print(f"📊 Smart Download Summary:")
        print(f"✅ Successful downloads: {results['success_count']}")
        print(f"❌ Failed downloads: {results['failed_count']}")
        print(f"⏭️ Duplicates skipped: {results['skipped_count']}")
        print(f"🔍 Total duplicates detected: {results['duplicates_count']}")
        print(f"📁 Files saved to: {downloader.output_path.absolute()}")
        print(f"⏱️ Total time: {results['total_time']:.1f} seconds")
        
        if results['duplicates_count'] > 0:
            print(f"\n🔍 Duplicate detection saved time by skipping {results['duplicates_count']} files")
        
        if results['failed_downloads']:
            print(f"\n❌ Failed URLs:")
            for item in results['failed_downloads']:
                retries = item.get('retries_attempted', 0)
                print(f"  • {item['url']} - {item['error']} (after {retries} retries)")
            print(f"\n💡 Use --resume to retry failed downloads")
        
        # Show statistics
        downloader.show_statistics()
        
        if results['failed_count'] > 0:
            sys.exit(1)
    
    print(f"\n🎉 Smart download completed successfully!")


if __name__ == "__main__":
    main()
