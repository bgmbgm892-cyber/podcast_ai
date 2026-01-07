# ---- src/rss_generator.py (UPDATED) ----
import os
import json
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from dotenv import load_dotenv
from config import EPISODES_DIR, RSS_BASE_URL, PODCAST_TITLE, PODCAST_LINK, PODCAST_DESCRIPTION, PODCAST_AUTHOR, PODCAST_EMAIL, PODCAST_IMAGE_URL, load_json

load_dotenv()

def save_episode_metadata(mp3_path, title, description, mp3_url=None):
    """Saves episode title and description to a JSON file next to the MP3."""
    base_name = os.path.basename(mp3_path).replace('.mp3', '.json')
    meta_path = os.path.join(EPISODES_DIR, base_name)
    data = {
        'title': title,
        'description': description,
        'mp3_path': os.path.basename(mp3_path),
        'mp3_url': mp3_url
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def build_feed():
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(PODCAST_TITLE)
    fg.link(href=PODCAST_LINK, rel='alternate')
    fg.description(PODCAST_DESCRIPTION)
    
    # Add iTunes-specific metadata required by Spotify
    fg.podcast.itunes_author(PODCAST_AUTHOR)
    fg.podcast.itunes_owner(name=PODCAST_AUTHOR, email=PODCAST_EMAIL)
    fg.podcast.itunes_image(PODCAST_IMAGE_URL)
    fg.podcast.itunes_category('News')

    # Iterate through files to build the feed
    for fname in sorted(os.listdir(EPISODES_DIR), reverse=True):
        if not fname.lower().endswith('.mp3'):
            continue
            
        path = os.path.join(EPISODES_DIR, fname)
        # Attempt to load saved metadata
        meta_name = fname.replace('.mp3', '.json')
        meta_path = os.path.join(EPISODES_DIR, meta_name)
        
        metadata = load_json(meta_path, default={})

        fe = fg.add_entry()
        fe.id(fname)
        
        # Use generated title/description, fall back to filename if missing
        fe.title(metadata.get('title', f"Episode: {fname}"))
        fe.description(metadata.get('description', f"New automated episode ({fname})."))
        
        # --- NEW: Set the Publish Date from the Filename ---
        # Filename format: episode_20260106T052419Z.mp3
        try:
            # Remove prefix and extension
            ts_str = fname.replace('episode_', '').replace('.mp3', '')
            # Parse the time string (YYYYMMDDTHHMMSSZ)
            dt = datetime.strptime(ts_str, '%Y%m%dT%H%M%SZ')
            # Set to UTC timezone
            dt = dt.replace(tzinfo=timezone.utc)
            fe.published(dt)
        except ValueError:
            # Fallback to file modification time if filename format is wrong
            file_ts = os.path.getmtime(path)
            dt = datetime.fromtimestamp(file_ts, tz=timezone.utc)
            fe.published(dt)
        # ---------------------------------------------------

        # Prefer an externally-hosted mp3_url saved in metadata (e.g., GitHub Release asset)
        mp3_url = metadata.get('mp3_url') or f"{RSS_BASE_URL}/{fname}"
        fe.enclosure(mp3_url, os.path.getsize(path), 'audio/mpeg')
    
    out = 'podcast.xml'
    fg.rss_file(out)
    return out

if __name__ == '__main__':
    print(build_feed())
