from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

from backend.src.agents.workflow_graph import run_full_pipeline
from backend.src.services.instagram_api import publish_image, InstagramAPIError
from backend.src.services.file_manager import (
    get_available_dates,
    load_trends_json,
    get_trend_by_topic,
    get_images_folder
)
from backend.src.config.settings import settings


class PublishRequest(BaseModel):
    date: str
    topic: str
    caption: Optional[str] = None


app = FastAPI()

origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")] if settings.BACKEND_CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate_memes")
def generate_memes(date: Optional[str] = None):
    """Generate memes for a specific date (defaults to today)"""
    try:
        result = run_full_pipeline(date)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/dates")
def get_dates():
    """Get list of available dates"""
    try:
        dates = get_available_dates()
        return {"dates": dates}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/trends")
def get_trends(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    """Get all trends for a specific date"""
    try:
        trends = load_trends_json(date)
        return {"date": date, "trends": trends}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/trend")
def get_trend(date: str = Query(..., description="Date in YYYY-MM-DD format"),
              topic: str = Query(..., description="Topic name")):
    """Get specific trend with image"""
    try:
        trend = get_trend_by_topic(date, topic)
        if not trend:
            raise HTTPException(status_code=404, detail="Trend not found")
        return trend
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/image/{date}/{topic}")
def get_image(date: str, topic: str):
    """Get image file for a specific date and topic"""
    try:
        images_folder = get_images_folder(date)
        # Sanitize topic for filename
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_topic = safe_topic.replace(' ', '_')[:50]
        
        image_path = images_folder / f"{safe_topic}.png"
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(str(image_path), media_type="image/png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/publish")
def publish(req: PublishRequest):
    """Publish meme to Instagram"""
    try:
        # Get trend data
        trend = get_trend_by_topic(req.date, req.topic)
        if not trend:
            raise HTTPException(status_code=404, detail="Trend not found")
        
        # Get image path
        image_path = trend.get("image_path")
        if not image_path or not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Upload image to GCP Storage first (if not already uploaded)
        from backend.src.services.gcp_storage import upload_file
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Upload to GCP and get public URL
        image_url = upload_file(image_bytes, f"{req.date}_{req.topic.replace(' ', '_')}.png")
        
        # Use provided caption or default from trend
        caption = req.caption or trend.get("caption", req.topic)
        
        # Publish to Instagram
        media_id = publish_image(image_url, caption)
        return {"status": "published", "media_id": media_id, "image_url": image_url}
    except HTTPException:
        raise
    except InstagramAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
