from google.cloud import storage
from backend.src.config.settings import settings

def upload_file(file_bytes, filename):
    client = storage.Client()
    bucket = client.bucket(settings.GCP_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(file_bytes)
    blob.make_public()
    return blob.public_url
