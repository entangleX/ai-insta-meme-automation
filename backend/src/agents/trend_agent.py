from google import genai
from google.genai import types
from backend.src.config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def fetch_market_trends():
    prompt = """
    Extract top trending topics for memes in India across:
    - political satire
    - social satire
    - international news
    - Bollywood / Pop culture
    - Social media controversies

    Return exactly 25 trends with short explanation.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[types.Part.from_text(prompt)],
        tools=[types.Tool(googleSearch=types.GoogleSearch())]
    )

    return response.text
