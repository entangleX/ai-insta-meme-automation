import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GCP_BUCKET = os.getenv("GCP_BUCKET_NAME")
    IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN") or os.getenv("INSTAGRAM_ACCESS_TOKEN")
    IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID") or os.getenv("INSTAGRAM_USER_ID")
    GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")
    IG_GRAPH_BASE = os.getenv("IG_GRAPH_BASE", "https://graph.facebook.com")
    BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS", "*")

settings = Settings()
