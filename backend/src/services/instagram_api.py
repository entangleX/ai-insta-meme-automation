import time
import requests
from backend.src.config.settings import settings
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


class InstagramAPIError(Exception):
    pass


def _base_url() -> str:
    return f"{settings.IG_GRAPH_BASE}/{settings.GRAPH_API_VERSION}"


def _auth_params() -> dict:
    if not settings.IG_ACCESS_TOKEN:
        raise InstagramAPIError("Missing IG access token")
    return {"access_token": settings.IG_ACCESS_TOKEN}


def create_media_container(image_url: str, caption: str) -> str:
    """
    Step 1: create container for image.
    """
    if not settings.IG_BUSINESS_ACCOUNT_ID:
        raise InstagramAPIError("Missing IG business account ID")

    url = f"{_base_url()}/{settings.IG_BUSINESS_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        **_auth_params(),
    }
    resp = requests.post(url, data=payload, timeout=30)
    if not resp.ok:
        logger.error("Failed to create IG media: %s", resp.text)
        raise InstagramAPIError(f"Media create failed: {resp.text}")
    data = resp.json()
    return data.get("id")


def publish_media(container_id: str) -> str:
    """
    Step 2: publish created container to feed.
    """
    url = f"{_base_url()}/{settings.IG_BUSINESS_ACCOUNT_ID}/media_publish"
    payload = {"creation_id": container_id, **_auth_params()}
    resp = requests.post(url, data=payload, timeout=30)
    if not resp.ok:
        logger.error("Failed to publish IG media: %s", resp.text)
        raise InstagramAPIError(f"Publish failed: {resp.text}")
    data = resp.json()
    return data.get("id")


def get_media_status(container_id: str) -> str:
    url = f"{_base_url()}/{container_id}"
    params = {"fields": "status,status_code", **_auth_params()}
    resp = requests.get(url, params=params, timeout=15)
    if not resp.ok:
        logger.error("Failed to fetch IG media status: %s", resp.text)
        raise InstagramAPIError(f"Status failed: {resp.text}")
    data = resp.json()
    return data.get("status_code")


def publish_image(image_url: str, caption: str, poll_seconds: int = 5, timeout_seconds: int = 90) -> str:
    """
    Create -> poll -> publish workflow. Returns published media ID.
    """
    container_id = create_media_container(image_url, caption)
    deadline = time.time() + timeout_seconds
    status = None
    while time.time() < deadline:
        status = get_media_status(container_id)
        if status == "FINISHED":
            break
        time.sleep(poll_seconds)
    if status != "FINISHED":
        raise InstagramAPIError(f"Media container not ready: {status}")
    media_id = publish_media(container_id)
    logger.info("Published IG media %s for image %s", media_id, image_url)
    return media_id
import requests

from backend.src.config.settings import settings


GRAPH_API_BASE = f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}"


class InstagramAPIError(RuntimeError):
    """Raised when Instagram Graph API returns an error."""


def _require_env():
    if not settings.IG_ACCESS_TOKEN or not settings.IG_BUSINESS_ACCOUNT_ID:
        raise InstagramAPIError(
            "Missing Instagram credentials. Set IG_ACCESS_TOKEN and IG_BUSINESS_ACCOUNT_ID env vars."
        )


def _handle_response(resp):
    if resp.status_code >= 300:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise InstagramAPIError(f"IG API error {resp.status_code}: {detail}")
    try:
        return resp.json()
    except Exception as exc:
        raise InstagramAPIError(f"IG API non-JSON response: {resp.text}") from exc


def create_media_container(image_url: str, caption: str) -> str:
    """Create a media container for an image URL."""
    _require_env()
    url = f"{GRAPH_API_BASE}/{settings.IG_BUSINESS_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": settings.IG_ACCESS_TOKEN,
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = _handle_response(resp)
    creation_id = data.get("id")
    if not creation_id:
        raise InstagramAPIError(f"Missing creation id in response: {data}")
    return creation_id


def publish_media(creation_id: str) -> str:
    """Publish a previously created media container."""
    _require_env()
    url = f"{GRAPH_API_BASE}/{settings.IG_BUSINESS_ACCOUNT_ID}/media_publish"
    payload = {"creation_id": creation_id, "access_token": settings.IG_ACCESS_TOKEN}
    resp = requests.post(url, data=payload, timeout=30)
    data = _handle_response(resp)
    media_id = data.get("id")
    if not media_id:
        raise InstagramAPIError(f"Missing media id in response: {data}")
    return media_id


def publish_image(image_url: str, caption: str) -> dict:
    """Create and publish an image in one step."""
    creation_id = create_media_container(image_url, caption)
    media_id = publish_media(creation_id)
    return {"creation_id": creation_id, "media_id": media_id}

