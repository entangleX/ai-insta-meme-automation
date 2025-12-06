from typing import Dict
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

# Mood mapping based on category
MOOD_MAP = {
    "politics": "satire",
    "scam": "sarcasm",
    "corruption": "serious",
    "viral_trend": "humorous",
    "bollywood": "humorous",
    "social_media": "sarcasm",
    "international_news": "serious",
    "viral": "humorous"
}

def determine_mood(category: str) -> str:
    """Determine mood based on category"""
    category_lower = category.lower()
    for key, mood in MOOD_MAP.items():
        if key in category_lower:
            return mood
    return "humorous"  # default

def generate_meme_prompt(topic: str, description: str, category: str) -> str:
    """
    Generate prompt for meme image creation based on topic, description, and mood.
    Ensures caption is included in the image.
    """
    mood = determine_mood(category)
    
    mood_instructions = {
        "satire": "Use satirical style with exaggerated features. Make it witty and thought-provoking.",
        "sarcasm": "Use sarcastic tone with ironic elements. Add subtle mockery.",
        "serious": "Use serious tone but keep it visually engaging. Convey the gravity of the issue.",
        "humorous": "Use light-hearted, funny style. Make it shareable and entertaining.",
        "sad": "Use empathetic tone. Convey emotion while keeping it appropriate for memes."
    }
    
    mood_style = mood_instructions.get(mood, mood_instructions["humorous"])
    
    prompt = f"""
Create a meme image for Instagram with the following requirements:

Topic: {topic}
Context: {description}
Category: {category}
Mood: {mood}

Style Requirements:
- {mood_style}
- Square format (1:1 aspect ratio) suitable for Instagram
- Bold, readable text/caption prominently displayed (top or bottom)
- Visually appealing and shareable
- Indian audience-friendly
- The caption should be: "{topic}" or a witty variation related to the topic

The image must include the caption text as part of the design. Make it eye-catching and meme-worthy.
"""
    
    return prompt.strip()

def generate_caption_for_image(topic: str, description: str, category: str) -> str:
    """Generate a caption text for the meme (to be used in Instagram post)"""
    mood = determine_mood(category)
    
    # Create a witty caption based on topic and mood
    if mood == "satire":
        return f"{topic} - When reality is stranger than fiction 😂"
    elif mood == "sarcasm":
        return f"{topic} - Because why not? 🤷‍♂️"
    elif mood == "serious":
        return f"{topic} - Something to think about 💭"
    elif mood == "humorous":
        return f"{topic} - The internet never disappoints 😄"
    else:
        return f"{topic} - Trending now 🔥"

