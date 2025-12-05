from google import genai
from google.genai import types
from backend.src.config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_meme_image(caption: str):
    prompt = f"""
    Create a meme template image suitable for Instagram.
    Style: funny / satire depending on caption mood.
    Caption: {caption}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_text(prompt)]
    )

    return response
