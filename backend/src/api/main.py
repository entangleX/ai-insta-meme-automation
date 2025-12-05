from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.src.agents.workflow_graph import run_full_pipeline
from backend.src.services.instagram_api import publish_image, InstagramAPIError
from backend.src.config.settings import settings


class PublishRequest(BaseModel):
    image_url: str
    caption: str


app = FastAPI()

origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")] if settings.BACKEND_CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/generate_memes")
def generate_memes():
    try:
        result = run_full_pipeline()
        return {"status": "success", "memes": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/publish")
def publish(req: PublishRequest):
    try:
        media_id = publish_image(req.image_url, req.caption)
        return {"status": "published", "media_id": media_id}
    except InstagramAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
