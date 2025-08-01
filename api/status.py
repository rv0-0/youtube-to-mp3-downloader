"""
Task status endpoint for Vercel
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, downloading, completed, failed
    progress: Optional[float] = None
    current_file: Optional[str] = None
    downloaded_files: List[str] = []
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# Simple in-memory storage (consider external storage for production)
download_tasks = {}

@app.get("/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a download task"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = download_tasks[task_id]
    return TaskStatus(**task)

@app.get("/", response_model=dict)
async def get_all_tasks():
    """Get all download tasks"""
    return {
        "tasks": list(download_tasks.values()),
        "total": len(download_tasks),
        "active": len([t for t in download_tasks.values() if t["status"] == "downloading"]),
        "completed": len([t for t in download_tasks.values() if t["status"] == "completed"]),
        "failed": len([t for t in download_tasks.values() if t["status"] == "failed"])
    }

# Export for Vercel
handler = app
