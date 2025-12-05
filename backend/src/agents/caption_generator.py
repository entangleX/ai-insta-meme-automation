from google import genai
from google.genai import types
from backend.src.config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_captions(topic):
    prompt = f"""
    Generate 5 highly viral meme captions about: {topic}
    Tone: Indian audience, witty, humorous, sarcasm allowed.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_text(prompt)]
    )
    return response.text.split("\n")
