import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from backend.src.agents.trend_agent import HotTopic
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

# Base directory for storing data
DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"

def get_date_folder(date_str: Optional[str] = None) -> Path:
    """Get or create date-wise folder"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    folder = DATA_DIR / date_str
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def get_images_folder(date_str: Optional[str] = None) -> Path:
    """Get or create date-wise images folder"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    folder = IMAGES_DIR / date_str
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_trends_json(trends: List[HotTopic], date_str: Optional[str] = None) -> str:
    """Save trends to JSON file in date-wise folder"""
    folder = get_date_folder(date_str)
    json_path = folder / "trends.json"

    # Convert HotTopic objects to dicts
    trends_data = [
        {
            "topic": trend.topic,
            "category": trend.category.value,  # Convert enum to string
            "description": trend.description,
            "fetched_at": datetime.now().isoformat()
        }
        for trend in trends
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str or datetime.now().strftime("%Y-%m-%d"),
            "total_trends": len(trends_data),
            "trends": trends_data
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(trends)} trends to {json_path}")
    return str(json_path)

def load_trends_json(date_str: str) -> List[Dict]:
    """Load trends from JSON file"""
    folder = get_date_folder(date_str)
    json_path = folder / "trends.json"

    if not json_path.exists():
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Handle both old format (list) and new format (dict with 'trends' key)
        if isinstance(data, list):
            return data
        return data.get("trends", [])

def save_meme_image(image_bytes: bytes, topic: str, date_str: Optional[str] = None) -> str:
    """Save meme image with topic name in date-wise folder"""
    folder = get_images_folder(date_str)
    
    # Sanitize topic name for filename
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
    
    image_path = folder / f"{safe_topic}.png"
    
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    
    logger.info(f"Saved image to {image_path}")
    return str(image_path)

def update_trend_with_image(topic: str, image_path: str, caption: str, date_str: Optional[str] = None):
    """Update trend JSON with image path and caption"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    trends = load_trends_json(date_str)
    
    for trend in trends:
        if trend["topic"] == topic:
            trend["image_path"] = image_path
            trend["caption"] = caption
            trend["generated"] = True
            break
    
    folder = get_date_folder(date_str)
    json_path = folder / "trends.json"
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)

def get_available_dates() -> List[str]:
    """Get list of available dates (folders)"""
    if not DATA_DIR.exists():
        return []
    
    dates = []
    for item in DATA_DIR.iterdir():
        if item.is_dir() and len(item.name) == 10 and item.name.count("-") == 2:
            dates.append(item.name)
    
    return sorted(dates, reverse=True)  # Most recent first

def get_trend_by_topic(date_str: str, topic: str) -> Optional[Dict]:
    """Get specific trend by date and topic"""
    trends = load_trends_json(date_str)
    for trend in trends:
        if trend["topic"] == topic:
            return trend
    return None

