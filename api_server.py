"""
FastAPI server for YouTube to MP3 downloader
Provides REST API endpoints for downloading YouTube videos as MP3 files
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, validator
import uvicorn

# Import our existing downloader modules
from youtube_to_mp3_smart import SmartYouTubeDownloader
from youtube_to_mp3_advanced import AdvancedYouTubeDownloader
from youtube_to_mp3 import download_youtube_to_mp3, batch_download_from_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="YouTube to MP3 API",
    description="REST API for downloading YouTube videos as MP3 files with smart features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for download tasks
download_tasks: Dict[str, Dict[str, Any]] = {}

# Wrapper functions for different downloader modes
def get_basic_downloader(output_dir: str, quality: int):
    """Basic downloader using functions from youtube_to_mp3.py"""
    class BasicDownloaderWrapper:
        def __init__(self, output_dir: str):
            self.output_dir = output_dir
        
        def download_video(self, url: str, quality: int = 192):
            try:
                result = download_youtube_to_mp3(url, self.output_dir, str(quality))
                return result
            except Exception as e:
                logger.error(f"Basic download failed: {e}")
                return False
        
        def download_single_video(self, url: str, thread_id: int = 0):
            """Interface compatibility with advanced/smart downloaders"""
            try:
                result = self.download_video(url)
                return (True, url, result) if result else (False, url, None)
            except Exception as e:
                return (False, url, str(e))
        
        def get_video_info(self, url: str):
            # Basic info extraction using yt-dlp
            import yt_dlp
            ydl_opts = {'quiet': True, 'no_warnings': True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            except Exception as e:
                logger.error(f"Failed to get video info: {e}")
                return None
    
    return BasicDownloaderWrapper(output_dir)

def get_advanced_downloader(output_dir: str, quality: int):
    """Advanced downloader using AdvancedYouTubeDownloader class"""
    return AdvancedYouTubeDownloader(output_dir, str(quality))

def get_smart_downloader(output_dir: str, quality: int):
    """Smart downloader using SmartYouTubeDownloader class"""
    return SmartYouTubeDownloader(output_dir, str(quality))

# Pydantic models for request/response
class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: Optional[int] = 192
    output_dir: Optional[str] = "downloads"
    mode: Optional[str] = "smart"  # basic, advanced, smart
    
    @validator('quality')
    def validate_quality(cls, v):
        if v not in [64, 128, 192, 256, 320]:
            raise ValueError('Quality must be one of: 64, 128, 192, 256, 320')
        return v
    
    @validator('mode')
    def validate_mode(cls, v):
        if v not in ['basic', 'advanced', 'smart']:
            raise ValueError('Mode must be one of: basic, advanced, smart')
        return v

class BatchDownloadRequest(BaseModel):
    urls: List[HttpUrl]
    quality: Optional[int] = 192
    output_dir: Optional[str] = "downloads"
    mode: Optional[str] = "smart"
    max_workers: Optional[int] = 3
    
    @validator('quality')
    def validate_quality(cls, v):
        if v not in [64, 128, 192, 256, 320]:
            raise ValueError('Quality must be one of: 64, 128, 192, 256, 320')
        return v
    
    @validator('max_workers')
    def validate_workers(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Max workers must be between 1 and 10')
        return v

class DownloadResponse(BaseModel):
    task_id: str
    status: str
    message: str
    url: Optional[str] = None
    estimated_time: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, downloading, completed, failed
    progress: Optional[float] = None
    current_file: Optional[str] = None
    downloaded_files: List[str] = []
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class VideoInfo(BaseModel):
    title: str
    duration: Optional[str] = None
    uploader: str
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "YouTube to MP3 API Server",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "download": "/download",
            "batch_download": "/batch-download",
            "status": "/status/{task_id}",
            "files": "/files",
            "info": "/info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_downloads": len([t for t in download_tasks.values() if t["status"] == "downloading"])
    }

@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Download a single YouTube video as MP3"""
    try:
        task_id = str(uuid.uuid4())
        
        # Create task entry
        download_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "url": str(request.url),
            "quality": request.quality,
            "mode": request.mode,
            "output_dir": request.output_dir,
            "progress": 0.0,
            "downloaded_files": [],
            "created_at": datetime.now(),
            "error_message": None
        }
        
        # Start background download
        background_tasks.add_task(
            download_single_video,
            task_id,
            str(request.url),
            request.quality,
            request.output_dir,
            request.mode
        )
        
        return DownloadResponse(
            task_id=task_id,
            status="pending",
            message="Download task started",
            url=str(request.url),
            estimated_time="1-3 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error starting download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start download: {str(e)}")

@app.post("/batch-download", response_model=DownloadResponse)
async def batch_download_videos(request: BatchDownloadRequest, background_tasks: BackgroundTasks):
    """Download multiple YouTube videos as MP3"""
    try:
        task_id = str(uuid.uuid4())
        urls = [str(url) for url in request.urls]
        
        # Create task entry
        download_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "urls": urls,
            "quality": request.quality,
            "mode": request.mode,
            "output_dir": request.output_dir,
            "max_workers": request.max_workers,
            "progress": 0.0,
            "downloaded_files": [],
            "total_files": len(urls),
            "created_at": datetime.now(),
            "error_message": None
        }
        
        # Start background batch download
        background_tasks.add_task(
            download_batch_videos,
            task_id,
            urls,
            request.quality,
            request.output_dir,
            request.mode,
            request.max_workers
        )
        
        estimated_time = f"{len(urls) * 2}-{len(urls) * 4} minutes"
        
        return DownloadResponse(
            task_id=task_id,
            status="pending",
            message=f"Batch download task started for {len(urls)} videos",
            estimated_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"Error starting batch download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch download: {str(e)}")

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_download_status(task_id: str):
    """Get the status of a download task"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = download_tasks[task_id]
    return TaskStatus(**task)

@app.get("/tasks")
async def get_all_tasks():
    """Get all download tasks"""
    return {
        "tasks": list(download_tasks.values()),
        "total": len(download_tasks),
        "active": len([t for t in download_tasks.values() if t["status"] == "downloading"]),
        "completed": len([t for t in download_tasks.values() if t["status"] == "completed"]),
        "failed": len([t for t in download_tasks.values() if t["status"] == "failed"])
    }

@app.get("/info")
async def get_video_info(url: str):
    """Get information about a YouTube video without downloading"""
    try:
        downloader = get_smart_downloader("temp", 192)
        info = await asyncio.get_event_loop().run_in_executor(
            None, downloader.get_video_info, url
        )
        
        if not info:
            raise HTTPException(status_code=404, detail="Video not found or unavailable")
        
        return VideoInfo(
            title=info.get('title', 'Unknown'),
            duration=info.get('duration_string', None),
            uploader=info.get('uploader', 'Unknown'),
            view_count=info.get('view_count', None),
            upload_date=info.get('upload_date', None),
            thumbnail=info.get('thumbnail', None),
            description=info.get('description', '')[:500] + '...' if info.get('description', '') else None
        )
        
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {str(e)}")

@app.get("/files")
async def list_downloaded_files(directory: str = "downloads"):
    """List all downloaded MP3 files"""
    try:
        downloads_dir = Path(directory)
        if not downloads_dir.exists():
            return {"files": [], "total": 0}
        
        mp3_files = []
        for file_path in downloads_dir.rglob("*.mp3"):
            stat = file_path.stat()
            mp3_files.append({
                "filename": file_path.name,
                "path": str(file_path.relative_to(downloads_dir)),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by creation time (newest first)
        mp3_files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "files": mp3_files,
            "total": len(mp3_files),
            "directory": str(downloads_dir.absolute())
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/download-file/{filename}")
async def download_file(filename: str, directory: str = "downloads"):
    """Download a specific MP3 file"""
    try:
        file_path = Path(directory) / filename
        
        if not file_path.exists() or not file_path.suffix.lower() == '.mp3':
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='audio/mpeg'
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str, directory: str = "downloads"):
    """Delete a specific MP3 file"""
    try:
        file_path = Path(directory) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path.unlink()
        return {"message": f"File {filename} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.post("/upload-urls")
async def upload_urls_file(file: UploadFile = File(...)):
    """Upload a text file containing YouTube URLs for batch download"""
    try:
        if not file.filename.endswith(('.txt', '.csv')):
            raise HTTPException(status_code=400, detail="Only .txt and .csv files are allowed")
        
        content = await file.read()
        urls = []
        
        for line in content.decode('utf-8').splitlines():
            line = line.strip()
            if line and (line.startswith('http://') or line.startswith('https://')):
                urls.append(line)
        
        return {
            "filename": file.filename,
            "urls_found": len(urls),
            "urls": urls[:10],  # Return first 10 URLs as preview
            "message": f"Found {len(urls)} valid URLs"
        }
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

# Background task functions
async def download_single_video(task_id: str, url: str, quality: int, output_dir: str, mode: str):
    """Background task for downloading a single video"""
    try:
        download_tasks[task_id]["status"] = "downloading"
        download_tasks[task_id]["progress"] = 10.0
        
        # Initialize downloader based on mode
        if mode == 'basic':
            downloader = get_basic_downloader(output_dir, quality)
        elif mode == 'advanced':
            downloader = get_advanced_downloader(output_dir, quality)
        else:  # smart
            downloader = get_smart_downloader(output_dir, quality)
        
        # Download the video
        download_tasks[task_id]["progress"] = 50.0
        result = await asyncio.get_event_loop().run_in_executor(
            None, downloader.download_video, url, quality
        )
        
        if result:
            download_tasks[task_id]["status"] = "completed"
            download_tasks[task_id]["progress"] = 100.0
            download_tasks[task_id]["downloaded_files"] = [result] if isinstance(result, str) else result
            download_tasks[task_id]["completed_at"] = datetime.now()
            logger.info(f"Download completed for task {task_id}: {url}")
        else:
            download_tasks[task_id]["status"] = "failed"
            download_tasks[task_id]["error_message"] = "Download failed"
            
    except Exception as e:
        download_tasks[task_id]["status"] = "failed"
        download_tasks[task_id]["error_message"] = str(e)
        logger.error(f"Download failed for task {task_id}: {str(e)}")

async def download_batch_videos(task_id: str, urls: List[str], quality: int, output_dir: str, mode: str, max_workers: int):
    """Background task for downloading multiple videos"""
    try:
        download_tasks[task_id]["status"] = "downloading"
        download_tasks[task_id]["progress"] = 0.0
        
        # Initialize downloader based on mode
        if mode == 'basic':
            downloader = get_basic_downloader(output_dir, quality)
        elif mode == 'advanced':
            downloader = get_advanced_downloader(output_dir, quality)
        else:  # smart
            downloader = get_smart_downloader(output_dir, quality)
        
        downloaded_files = []
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            try:
                download_tasks[task_id]["current_file"] = url
                download_tasks[task_id]["progress"] = (i / total_urls) * 100
                
                result = await asyncio.get_event_loop().run_in_executor(
                    None, downloader.download_video, url, quality
                )
                
                if result:
                    if isinstance(result, str):
                        downloaded_files.append(result)
                    else:
                        downloaded_files.extend(result)
                
                download_tasks[task_id]["downloaded_files"] = downloaded_files
                
            except Exception as e:
                logger.error(f"Failed to download {url}: {str(e)}")
                continue
        
        download_tasks[task_id]["status"] = "completed"
        download_tasks[task_id]["progress"] = 100.0
        download_tasks[task_id]["completed_at"] = datetime.now()
        download_tasks[task_id]["current_file"] = None
        
        logger.info(f"Batch download completed for task {task_id}: {len(downloaded_files)}/{total_urls} files")
        
    except Exception as e:
        download_tasks[task_id]["status"] = "failed"
        download_tasks[task_id]["error_message"] = str(e)
        logger.error(f"Batch download failed for task {task_id}: {str(e)}")

# Cleanup old tasks (run periodically)
@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("YouTube to MP3 API Server starting up...")
    
    # Create downloads directory if it doesn't exist
    Path("downloads").mkdir(exist_ok=True)
    
    logger.info("API Server ready!")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
