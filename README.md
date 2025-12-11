# Podcast AI — Automated Podcast Generator

Generate, publish, and distribute podcast episodes automatically using AI. Fetches trending topics, generates Host+Guest discussion scripts with Gemini, synthesizes audio with gTTS, and publishes to GitHub Releases — ready for Spotify, Apple Podcasts, and other platforms.

## Features

✅ **Automated Topic Discovery**: Uses Gemini to fetch current trending topics with search grounding.  
✅ **AI Script Generation**: Generates structured Host+Guest discussion scripts using Gemini.  
✅ **Audio Synthesis**: Converts scripts to MP3 audio (local gTTS; upgradeable to Gemini TTS or ElevenLabs).  
✅ **GitHub Publishing**: Auto-uploads episodes to GitHub Releases (free hosting).  
✅ **RSS Feed Generation**: Creates a valid podcast RSS feed for Spotify/Apple/other platforms.  
✅ **Scheduled Automation**: Run daily via cron to publish new episodes automatically.  
✅ **Zero Cost (with free tier)**: Uses Gemini Pro (you likely have this), local gTTS, GitHub (all free).

## Quick Start (5 minutes)

### 1. Clone & Setup

```bash
cd /home/labuser/podcast_ai
source venv/bin/activate
pip install -r requirements.txt  # already installed if you ran setup.sh
```

### 2. Configure `.env`

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Gemini API Key (get from https://ai.google.com/studio)
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Publishing (follow SETUP_GITHUB.md)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=yourusername/yourrepo

# Optional: customize podcast metadata
PODCAST_TITLE=My Automated Daily Brief
PODCAST_DESCRIPTION=AI-generated podcast covering trending topics daily.
RSS_BASE_URL=https://yourusername.github.io/yourrepo
EPISODES_DIR=episodes

# Optional: use Gemini TTS instead of gTTS (set to 1 if available in your plan)
# USE_GEMINI_TTS=0
```

**Important**: Never commit `.env` to git. It's already in `.gitignore`.

### 3. Generate Your First Episode

```bash
python3 src/main_runner.py --once
```

**Output:**
- `episodes/script_*.txt` — generated discussion script
- `episodes/episode_*.mp3` — synthesized audio
- `podcast.xml` — updated RSS feed
- Episode uploaded to GitHub Release (if `GITHUB_TOKEN` is set)

### 4. Publish to Spotify / Apple Podcasts

See **SETUP_GITHUB.md** for step-by-step instructions:
1. Enable GitHub Pages on your repo.
2. Submit your RSS URL (`https://yourusername.github.io/yourrepo/podcast.xml`) to Spotify/Apple.
3. New episodes will appear automatically.

### 5. (Optional) Schedule Daily Generation

Add to your crontab:

```bash
crontab -e
```

Add this line:

```cron
0 6 * * * cd /home/labuser/podcast_ai && /home/labuser/podcast_ai/venv/bin/python3 src/main_runner.py >> /home/labuser/podcast_ai/automation.log 2>&1
```

Now episodes will be generated daily at 6 AM.

## Project Structure

```
podcast_ai/
├── src/
│   ├── main_runner.py           # Main orchestrator
│   ├── topic_fetcher.py         # Fetch trending topics (Gemini)
│   ├── generator.py             # Generate scripts (Gemini / fallback)
│   ├── tts.py                   # Text-to-speech (gTTS; upgradeable)
│   ├── rss_generator.py         # Build podcast RSS feed
│   ├── utils.py                 # Helpers (publish_local, timestamp, etc.)
│   ├── uploader.py              # Wrapper for publish_local
│   ├── github_uploader.py       # Upload to GitHub Releases
│   ├── config.py                # Configuration & constants
│   └── __pycache__/
├── episodes/                    # Generated scripts & MP3s (local)
├── topics/                      # Topic cache (optional)
├── venv/                        # Python virtual environment
├── .env                         # Configuration (local, not committed)
├── .env.example                 # Example configuration template
├── .gitignore                   # Excludes .env, venv/, etc.
├── requirements.txt             # Python dependencies
├── setup.sh                     # Initialization script
├── README.md                    # This file
├── SETUP_GITHUB.md              # GitHub publishing guide
└── podcast.xml                  # Generated RSS feed (committed or published via GitHub Pages)
```

## Configuration

See `.env.example` for all available options:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | Yes | (none) | Google Gemini API key for topic fetching & script generation |
| `GITHUB_TOKEN` | No | (none) | GitHub PAT for uploading episodes to releases |
| `GITHUB_REPO` | No | (none) | GitHub repo in format `owner/repo` |
| `PODCAST_TITLE` | No | "Automated Daily Brief" | Podcast title for RSS |
| `PODCAST_DESCRIPTION` | No | "Auto-generated briefings" | Podcast description for RSS |
| `RSS_BASE_URL` | No | "http://localhost:8000" | Base URL for RSS enclosures (e.g., GitHub Pages URL) |
| `EPISODES_DIR` | No | "episodes" | Directory to store generated episodes |
| `USE_GEMINI_TTS` | No | 0 | Set to 1 to use Gemini TTS (if available in your plan) |

## Usage

### Generate a Single Episode

```bash
python3 src/main_runner.py --once
```

### Run Scheduled Generation (Default: Daily at 6 AM)

```bash
python3 src/main_runner.py
```

(Runs continuously; check logs or use cron instead for production.)

### Check Generated Episodes

```bash
ls -lh episodes/
cat episodes/podcast.xml
```

## How It Works

1. **Topic Fetching** (`topic_fetcher.py`)
   - Calls Gemini API with search grounding to find the most discussed current event.
   - Falls back to hardcoded topics if Gemini is unavailable.

2. **Script Generation** (`generator.py`)
   - Sends the topic to Gemini with a prompt requesting a Host+Guest discussion script.
   - Falls back to OpenAI or a simple local template if Gemini is unavailable.
   - Returns structured data: `{title, description, script}`.

3. **Audio Synthesis** (`tts.py`)
   - Splits the script into segments (by speaker labels: Host/Guest).
   - Uses gTTS to synthesize each segment to an MP3.
   - Combines segments with silence gaps.
   - Normalizes and exports the final MP3.

4. **Publishing** (`utils.py` + `github_uploader.py`)
   - Saves the script and metadata in `episodes/`.
   - (Optional) Uploads the MP3 to a GitHub Release.
   - Saves metadata with the external URL (if available).
   - Regenerates `podcast.xml` RSS feed with all episodes.

5. **Distribution** (Manual)
   - Publish `podcast.xml` via GitHub Pages (free, stable URL).
   - Submit RSS URL to Spotify, Apple Podcasts, etc. (one-time).
   - New episodes appear automatically in all platforms within hours.

## Costs & Free Tier

| Component | Cost | Notes |
|-----------|------|-------|
| Gemini (Script + Topic) | Included in Pro plan | You likely have this already |
| gTTS (Audio) | Free | Single voice, good quality for testing |
| GitHub (Hosting) | Free | Free for small-scale (< 1 GB/month typical) |
| Spotify/Apple | Free | One-time submission; no ongoing fees |
| **Total Additional Cost** | **$0** | Within free/existing tiers |

### Optional Paid Upgrades (when ready)

- **Gemini TTS** (higher quality): Included in Gemini Pro; check if available in your plan.
- **ElevenLabs TTS** (multi-voice, premium quality): ~$5–50/month depending on usage.
- **S3/Cloud Storage** (if hosting many episodes): ~$0.05–1/month for small scale.

## Troubleshooting

### "ImportError: cannot import name X from Y"
- Ensure you're in the venv: `source venv/bin/activate`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### "Gemini client not initialized"
- `GEMINI_API_KEY` is not set or invalid.
- The script will fall back to local generation (slower/less quality).
- Get a Gemini API key: https://ai.google.com/studio → "Get API Key"

### "GitHub upload failed"
- Check `GITHUB_TOKEN` and `GITHUB_REPO` are set in `.env`.
- Verify the token has `repo` or `public_repo` scope.
- Test: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`

### "No audio parts generated"
- The script may be empty or not parsed correctly.
- Check the saved script in `episodes/script_*.txt`.
- Ensure the script contains recognizable text.

### "RSS feed not updating in Spotify/Apple"
- Wait 24–48 hours for initial sync.
- Re-check the RSS URL in Spotify/Apple settings.
- Verify `podcast.xml` is publicly accessible: `curl https://yourusername.github.io/yourrepo/podcast.xml`

## Next Steps

- **Start publishing**: Follow SETUP_GITHUB.md to enable GitHub publishing and submit to Spotify.
- **Improve audio**: Swap gTTS for Gemini TTS (if available) or ElevenLabs (for multi-voice).
- **Customize scripts**: Edit `src/generator.py` to change the prompt and add domain-specific logic.
- **Monitor & iterate**: Check `automation.log` if running via cron to debug issues.

## Development

### Adding a New TTS Provider

Edit `src/tts.py` and add a new function (e.g., `synthesize_gemini_tts()`). Then update `synthesize()` to call it based on an env var.

### Customizing Script Generation

Edit the prompt in `src/generator.py`'s `generate_prompt()` function. For example, you can:
- Ask for a specific tone (e.g., "technical", "casual").
- Request structured segments (e.g., "Explain what it is, then discuss 3 impacts").
- Add domain-specific prompts (e.g., "Focus on business implications").

### Using a Different Topic Source

Edit `src/topic_fetcher.py` to fetch from a custom news API (e.g., NewsAPI, Reddit, Twitter) instead of (or in addition to) Gemini.

## Support & Contributions

For issues, bug reports, or feature requests, create an issue in your GitHub repo or contact the project maintainer.

---

**Happy podcasting!** 🎙️📻
