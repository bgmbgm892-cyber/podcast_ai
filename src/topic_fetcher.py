# ---- src/topic_fetcher.py (MODIFIED) ----
import os
import random
import json
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TOPICS_CACHE = 'topics/topics_cache.json'

if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
    except Exception:
        client = None
else:
    client = None


def fetch_trending_topic_from_gemini():
    """Uses the Gemini API with Search Grounding to find a top trend."""
    if not client:
        print("Gemini client not initialized. Falling back to local data.")
        return []

    prompt = (
        "Identify the single most compelling and discussed current events topic globally or in technology/business. "
        "Summarize the topic in a concise sentence. Do NOT add any extra text or conversation."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                # Enable Google Search grounding tool
                tools=[{"google_search": {}}]
            )
        )
        topic = response.text.strip()
        
        # Simple cache update (you can make this more robust)
        # Note: We don't save to the cache here as this function is now the primary source.
        
        return [topic] if topic else []
        
    except Exception as e:
        print(f"Gemini topic fetch failed: {e}")
        return []

def pick_random_trending():
    """Picks a random topic from the fetched candidates or uses a fallback."""
    # 1. Try fetching live data from Gemini
    items = fetch_trending_topic_from_gemini()
    
    # 2. If Gemini fails, fall back to the last cached topics
    if not items:
        # Import load_json from utils here if needed, or rely on hardcoded fallback
        items = ['latest global technology trends', 'recent space exploration news'] # Hardcoded fallback
    
    return random.choice(items) if items else 'latest global technology trends'

if __name__ == '__main__':
    print(pick_random_trending())