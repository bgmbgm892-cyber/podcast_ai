"""Configuration constants for the podcast automation."""
import os
import json
from dotenv import load_dotenv

load_dotenv()

EPISODES_DIR = os.getenv('EPISODES_DIR', 'episodes')
RSS_BASE_URL = os.getenv('RSS_BASE_URL', 'http://localhost:8000')
PODCAST_TITLE = os.getenv('PODCAST_TITLE', 'Automated Daily Brief')
PODCAST_LINK = os.getenv('PODCAST_LINK', RSS_BASE_URL)
PODCAST_DESCRIPTION = os.getenv('PODCAST_DESCRIPTION', 'Automatically generated news briefings.')


def load_json(path, default=None):
    """Load a JSON file, returning default if it doesn't exist or errors."""
    if default is None:
        default = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

