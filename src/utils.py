"""Utility helpers for the podcast automation.

Provides simple filesystem helpers and the `publish_local` function used by the runner.
"""
import os
import json
from shutil import copyfile
from datetime import datetime
from dotenv import load_dotenv
from config import EPISODES_DIR, load_json
from rss_generator import build_feed, save_episode_metadata
from github_uploader import upload_release_asset

load_dotenv()


def timestamp():
    """Return a short timestamp suitable for filenames."""
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def save_json(path, data):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def publish_local(mp3_path, title, description):
    """Copy an MP3 into `EPISODES_DIR`, save metadata and regenerate RSS."""
    os.makedirs(EPISODES_DIR, exist_ok=True)
    basename = os.path.basename(mp3_path)
    dest = os.path.join(EPISODES_DIR, basename)

    # 1. Copy the MP3 — avoid copying onto itself if paths are identical
    try:
        src_abs = os.path.abspath(mp3_path)
        dest_abs = os.path.abspath(dest)
        if src_abs != dest_abs:
            copyfile(mp3_path, dest)
        else:
            # already in place; nothing to copy
            pass
    except Exception as e:
        # If copy fails, raise a clearer error
        raise RuntimeError(f"Failed to copy mp3 file: {e}")

    # 2. Optionally upload to GitHub Releases and save metadata (next to the mp3)
    mp3_url = None
    try:
        # upload_release_asset returns browser_download_url or None
        mp3_url = upload_release_asset(dest)
    except Exception:
        mp3_url = None

    save_episode_metadata(dest, title, description, mp3_url=mp3_url)

    # 3. Regenerate the feed
    build_feed()
    return dest


if __name__ == '__main__':
    print('utils module loaded')