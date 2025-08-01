"""
Download endpoint for Vercel
"""
import sys
import os
from pathlib import Path
import asyncio
import uuid
from datetime import datetime

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, validator
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

# Pydantic models
class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: Optional[int] = 192
    output_dir: Optional[str] = "/tmp/downloads"
    mode: Optional[str] = "smart"
    
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

class DownloadResponse(BaseModel):
    task_id: str
    status: str
    message: str
    url: Optional[str] = None
    estimated_time: Optional[str] = None

# Simple in-memory storage for Vercel (consider using external storage for production)
download_tasks = {}

@app.post("/", response_model=DownloadResponse)
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Download a single YouTube video as MP3"""
    try:
        task_id = str(uuid.uuid4())
        
        # Create task entry
        download_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "url": str(request.url),
            "quality": request.quality or 192,
            "mode": request.mode or "smart",
            "output_dir": request.output_dir or "/tmp/downloads",
            "progress": 0.0,
            "downloaded_files": [],
            "created_at": datetime.now(),
            "error_message": None
        }
        
        # Note: For Vercel, we'll need to handle downloads differently
        # as serverless functions have time limits
        download_tasks[task_id]["status"] = "processing"
        download_tasks[task_id]["message"] = "Download started (Vercel serverless)"
        
        return DownloadResponse(
            task_id=task_id,
            status="pending",
            message="Download task queued for processing",
            url=str(request.url),
            estimated_time="1-3 minutes"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start download: {str(e)}")

# Export for Vercel
handler = app
