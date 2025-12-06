import os
import json
from enum import Enum
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

from google import genai
from google.genai import types

load_dotenv()


# ==============
#  Pydantic Model
# ==============

class TopicCategory(str, Enum):
    politics = "politics"
    scam = "scam"
    corruption = "corruption"
    social = "social"
    entertainment = "entertainment"
    international = "international"
    tech_ai = "tech_ai"
    economy = "economy"
    other = "other"


class HotTopic(BaseModel):
    topic: str          # 3–5 words
    category: TopicCategory
    description: str    # <= 60 words


# ==============
#  Gemini client
# ==============

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.6,
)


# ==============
#  Tool: Web trend search using Gemini+GoogleSearch
# ==============

class SocialTrendTool(BaseTool):
    """
    Tool that uses Gemini + GoogleSearch to summarize what's hot on the
    internet & social media for a given region/niche.
    """
    name: str = "Social Trend Fetcher"
    description: str = (
        "Search the internet and summarize current hot topics on social media, news, "
        "and general internet discussion, for a given region or niche."
    )

    def _run(self, query: str) -> str:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are a trend researcher for an internet meme/news page.

Task:
- Look at CURRENT trends on social media, news, and online discussions.
- Focus on {query}.
- Return around 25–30 candidate topics that are being widely discussed now.

For each candidate topic, include:
- short title
- category: politics, scam, corruption, social, entertainment, international, tech_ai, economy, other
- 1–2 sentence context

Return STRICTLY in JSON as a list of objects:
[
  {{
    "topic": "...",
    "category": "...",
    "context": "..."
  }},
  ...
]
"""

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Part.from_text(text=prompt)],
            tools=[types.Tool(googleSearch=types.GoogleSearch())],
        )

        text = resp.text or "[]"
        return text


social_trend_tool = SocialTrendTool()


# ==============
#  Agents
# ==============

trend_researcher = Agent(
    role="Internet Trend Researcher",
    goal=(
        "Discover currently hot topics on the internet and social media, "
        "with a focus on what people in India and globally are actively discussing."
    ),
    backstory=(
        "You constantly scan Twitter(X), Instagram, Reddit, and news sites, "
        "and are very good at spotting what is trending right now."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[social_trend_tool],
    llm=gemini_llm,
)

topic_selector = Agent(
    role="Hot Topic Selector",
    goal=(
        "From a broader list of candidate topics, select the single top 10 "
        "most trending, impactful, and internet-hot topics, and format them "
        "for downstream use in an app."
    ),
    backstory=(
        "You understand what goes truly viral. You focus on big scandals, "
        "political fights, scams, corruption stories, social debates, "
        "entertainment buzz, international news and tech/AI headlines."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm,
)


# ==============
#  Tasks
# ==============

trend_task = Task(
    description=(
        "1) Use the Social Trend Fetcher tool with an appropriate query like "
        "'current hot internet and social media topics for India and global'.\n"
        "2) Get around 25–30 candidate topics with fields: topic, category, context.\n"
        "3) Return the tool output without changing the JSON structure."
    ),
    expected_output=(
        "Raw JSON string: a list of objects with fields topic, category, context."
    ),
    agent=trend_researcher,
)

selection_task = Task(
    description=(
        "You receive JSON with ~25–30 candidate topics (fields: topic, category, context).\n"
        "Your job:\n"
        "- Analyze which topics are truly HOT on the internet right now.\n"
        "- Choose exactly the top 10.\n\n"
        "For the final output, you MUST return STRICT JSON ONLY (no explanation text), "
        "as a list of 10 objects with fields:\n"
        "- topic: 3–5 words ONLY, short but clear (no hashtags, no quotes).\n"
        "- category: one of [politics, scam, corruption, social, entertainment, "
        "international, tech_ai, economy, other].\n"
        "- description: under 60 words, explaining what the topic is and why it is hot.\n\n"
        "Example of ONE object:\n"
        "{{\n"
        "  \"topic\": \"New election funding scandal\",\n"
        "  \"category\": \"corruption\",\n"
        "  \"description\": \"A major political party is under fire for alleged hidden funding...\"\n"
        "}}\n\n"
        "Return ONLY the JSON array with 10 such objects. Do NOT wrap in backticks or prose."
    ),
    expected_output=(
        "JSON array with exactly 10 objects: topic (3–5 words), category, description (<60 words)."
    ),
    agent=topic_selector,
)


# ==============
#  Crew
# ==============

hot_topics_crew = Crew(
    agents=[trend_researcher, topic_selector],
    tasks=[trend_task, selection_task],
    process=Process.sequential,
    verbose=True,
)


# ==============
#  Runner + Parser
# ==============

def run_hot_topics_crew(region_query: str = "Indian and global internet"):
    """
    Runs the crew and returns a list of HotTopic objects.

    region_query: describes the region / niche to target trends for.
    """
    result = hot_topics_crew.kickoff(inputs={"region": region_query})

    # Depending on CrewAI version, 'result' might be a string or an object.
    # We'll coerce to string and try to parse JSON from it.
    result_text = str(result)

    # Try to find JSON (if model adds extra text). Simplest: assume pure JSON.
    try:
        data = json.loads(result_text)
    except json.JSONDecodeError:
        # Very basic fallback: try to extract the first JSON block
        start = result_text.find("[")
        end = result_text.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("Could not find JSON array in model output")
        json_str = result_text[start:end]
        data = json.loads(json_str)

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array from the model")

    hot_topics: List[HotTopic] = []
    for item in data:
        try:
            hot_topics.append(HotTopic(**item))
        except ValidationError as e:
            print("Validation failed for item, skipping:", item)
            print(e)

    return hot_topics


def fetch_market_trends(region_query: str = "Indian and global internet"):
    """
    Main function to fetch trends using CrewAI agents.
    Returns a list of HotTopic objects for use in the application.
    Saving to JSON is handled by the workflow_graph using file_manager.
    """
    # Get trends from CrewAI
    hot_topics = run_hot_topics_crew(region_query)
    return hot_topics


if __name__ == "__main__":
    topics = run_hot_topics_crew("current hot topics for Indian internet and social media")
    for i, t in enumerate(topics, start=1):
        print(f"{i}. [{t.category}] {t.topic} -> {t.description}")
