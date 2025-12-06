import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root (where .env should be)
# Go up from backend/src/config to project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"

# Load .env from project root
import sys
if env_path.exists():
    print(f"Loading .env from: {env_path}", file=sys.stderr, flush=True)
    
    # Try to read first few lines of .env to debug
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]
            print(f"First 5 lines of .env:", file=sys.stderr, flush=True)
            for i, line in enumerate(lines, 1):
                # Mask sensitive data but show structure
                if '=' in line:
                    key = line.split('=')[0].strip()
                    print(f"  Line {i}: {key}=...", file=sys.stderr, flush=True)
                else:
                    print(f"  Line {i}: {line.strip()}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Error reading .env: {e}", file=sys.stderr, flush=True)
    
    result = load_dotenv(dotenv_path=env_path, override=True)
    print(f"load_dotenv returned: {result}", file=sys.stderr, flush=True)
    
    # Debug: Show all env vars that start with GEMINI or OPENROUTER
    print("\nEnvironment variables found:", file=sys.stderr, flush=True)
    found_any = False
    for key, value in os.environ.items():
        if 'GEMINI' in key.upper() or 'OPENROUTER' in key.upper():
            found_any = True
            if value:
                print(f"  {key} = {value[:20]}... (length: {len(value)})", file=sys.stderr, flush=True)
            else:
                print(f"  {key} = (empty)", file=sys.stderr, flush=True)
    if not found_any:
        print("  No GEMINI or OPENROUTER variables found!", file=sys.stderr, flush=True)
else:
    print(f"WARNING: .env file not found at: {env_path}", file=sys.stderr, flush=True)
    # Try loading from current directory as fallback
    load_dotenv(override=True)

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or 'AIzaSyBqWMxHMSN4uVEc08-bUqphSHc34jRz7OA'  # TODO: Remove hardcoded fallback once .env is fixed
    GCP_BUCKET = os.getenv("GCP_BUCKET_NAME")
    IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN") or os.getenv("INSTAGRAM_ACCESS_TOKEN")
    IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID") or os.getenv("INSTAGRAM_USER_ID")
    GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")
    IG_GRAPH_BASE = os.getenv("IG_GRAPH_BASE", "https://graph.facebook.com")
    BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS", "*")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

settings = Settings()

# Debug: Print what we got
print(f"GEMINI_API_KEY loaded: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
if settings.GEMINI_API_KEY:
    print(f"GEMINI_API_KEY length: {len(settings.GEMINI_API_KEY)}")
    print(f"GEMINI_API_KEY starts with: {settings.GEMINI_API_KEY[:10]}...")

# Validate on import
if not settings.GEMINI_API_KEY:
    raise ValueError(
        f"GEMINI_API_KEY is required but not found.\n"
        f"Check .env file at: {env_path}\n"
        f"Make sure it contains: GEMINI_API_KEY=your_key_here\n"
        f"File exists: {env_path.exists()}"
    )
