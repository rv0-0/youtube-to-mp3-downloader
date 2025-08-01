"""
Get video info endpoint for Vercel
"""
import sys
import os
from pathlib import Path
import asyncio

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoInfo(BaseModel):
    title: str
    duration: Optional[str] = None
    uploader: str
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None

@app.get("/", response_model=VideoInfo)
async def get_video_info(url: str):
    """Get information about a YouTube video without downloading"""
    try:
        # Basic video info extraction using yt-dlp
        import yt_dlp
        
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'extract_flat': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
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
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {str(e)}")

# Export for Vercel
handler = app
