# ---- src/main_runner.py (MODIFIED) ----
"""
Orchestrator: pick topic -> generate script -> synthesize -> publish
Run with: python3 src/main_runner.py --once
"""
import argparse
import os
import sys

# Ensure `src` directory is importable when running `python3 src/main_runner.py`
sys.path.insert(0, os.path.dirname(__file__))

from topic_fetcher import pick_random_trending
from generator import generate_script
from tts import synthesize
from utils import timestamp, publish_local


def run_once():
    topic = pick_random_trending()
    print('Selected topic:', topic)
    
    # Get structured output: title, description, and script
    podcast_data = generate_script(topic, minutes=8)
    script = podcast_data['script']
    title = podcast_data['title']
    description = podcast_data['description']
    
    # 1. Save script
    os.makedirs('episodes', exist_ok=True)
    script_file = f"episodes/script_{timestamp()}.txt"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    print('Script saved to', script_file)
    
    # 2. Generate Audio
    mp3 = synthesize(script, out_path=f"episodes/episode_{timestamp()}.mp3")
    print('Audio generated:', mp3)
    
    # 3. Publish (copies file, saves metadata, regenerates RSS)
    published = publish_local(mp3, title, description)
    print(f'Podcast published. Title: "{title}". Location: {published}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    
    # *** CRITICAL FIX: Running the script directly is correct: `python3 src/main_runner.py` ***
    
    if args.once:
        run_once()
    else:
        # simple scheduler
        import schedule, time
        schedule.every().day.at("06:00").do(run_once)
        while True:
            schedule.run_pending()
            time.sleep(10)