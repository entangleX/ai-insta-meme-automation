# AI Insta Meme Automation

End-to-end prototype that:
- discovers trends and generates captions/images with Gemini,
- uploads generated images to GCP Storage,
- publishes selected images with captions to Instagram via Graph API,
- provides a React/Vite dashboard to generate and publish.

## Prerequisites
- Python 3.10+ (3.11 recommended)
- Node 18+ (Node 20 used in Dockerfile)
- Git, npm
- GCP project + bucket (public read) + service account if needed
- Instagram Graph API access (access token + business account ID)

## Setup
```powershell
git clone https://github.com/YOUR_USER/ai-insta-meme-automation.git
cd ai-insta-meme-automation
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

### Environment (.env in repo root)
```
GEMINI_API_KEY=your_gemini_key
GCP_BUCKET_NAME=your_gcs_bucket
IG_ACCESS_TOKEN=your_ig_access_token
IG_BUSINESS_ACCOUNT_ID=your_ig_business_account_id
GRAPH_API_VERSION=v21.0
BACKEND_CORS_ORIGINS=http://localhost:5174
# Optional if using service account for GCS:
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Frontend (optional `.env` or `.env.local` under `frontend/`):
```
VITE_API_URL=http://localhost:8000
```

## Run Backend (FastAPI)
```powershell
uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000
```
Endpoints:
- `GET /generate_memes` – trend → topics → captions → images → GCS upload → returns topics/captions/image URLs.
- `POST /publish` – `{ image_url, caption }` publishes to Instagram via Graph API container → publish flow.

## Run Frontend (React/Vite)
```powershell
cd frontend
npm install
npm run dev -- --host --port 5174
```
Open http://localhost:5174 (or the Network URL Vite prints).

## Docker Compose
From repo root:
```powershell
docker-compose up
```
Ports: backend 8000, frontend 5173 (adjust `VITE_API_URL` if needed).

## Notes / Troubleshooting
- Gemini key required: ensure `GEMINI_API_KEY` is set before starting backend.
- Instagram: `IG_ACCESS_TOKEN` and `IG_BUSINESS_ACCOUNT_ID` must be valid; backend uses create-container → publish flow.
- CORS: set `BACKEND_CORS_ORIGINS` to your frontend origin (e.g., `http://localhost:5174`).
- If frontend shows “Network Error”, confirm backend is up on the same URL/port and check backend logs for exceptions.
- Python version warning: google api_core will deprecate 3.10 in the future; prefer 3.11+.

