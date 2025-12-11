# GitHub Publishing Setup Guide

This guide shows how to publish your generated podcast episodes to GitHub Releases (free hosting) and submit the RSS feed to Spotify/Apple Podcasts.

## Step 1: Create a GitHub Personal Access Token (PAT)

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name (e.g., `podcast-ai`)
4. Select scopes:
   - If your repo is **public**: select only `public_repo`
   - If your repo is **private**: select `repo` (full control)
5. Click **"Generate token"** at the bottom
6. **Copy the token immediately** (you won't see it again)

## Step 2: Add Token to `.env`

In your `/home/labuser/podcast_ai/.env` file, add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=yourusername/yourrepo
```

**Important**: 
- Replace `ghp_xxxxx` with your actual token.
- Replace `yourusername/yourrepo` with your GitHub repo (e.g., `john-doe/podcast-ai`).
- **Never commit `.env`** to git — keep it local and in `.gitignore`.

## Step 3: Test the Pipeline

Run the podcast generator with GitHub publishing enabled:

```bash
cd /home/labuser/podcast_ai
source venv/bin/activate
python3 src/main_runner.py --once
```

**Expected output:**
- A script will be generated and saved in `episodes/script_*.txt`.
- An MP3 will be synthesized in `episodes/episode_*.mp3`.
- The MP3 will be uploaded to a GitHub Release (auto-created with tag `automated`).
- A new `podcast.xml` RSS feed will be generated pointing to the GitHub Release asset URL.

You should see output like:
```
Selected topic: [current trending topic]
Script saved to episodes/script_YYYYMMDDTHHMMSSZ.txt
Audio generated: episodes/episode_YYYYMMDDTHHMMSSZ.mp3
Podcast published. Title: "Daily Brief: [topic]". Location: episodes/episode_YYYYMMDDTHHMMSSZ.mp3
```

## Step 4: Enable GitHub Pages (for RSS URL)

So Spotify/Apple can read your RSS feed via a stable URL, enable GitHub Pages:

1. Go to your GitHub repo → **Settings** → **Pages**
2. Under "Build and deployment":
   - Select **Source**: `Deploy from a branch`
   - Select **Branch**: `main` (or your default branch)
   - Select **Folder**: `/ (root)` or `/docs` if you want to keep it separate
3. Click **Save**
4. GitHub will show you a URL like: `https://yourusername.github.io/yourrepo/`

Your RSS feed will be available at: `https://yourusername.github.io/yourrepo/podcast.xml`

## Step 5: Submit RSS to Spotify

1. Go to **Spotify for Podcasters**: https://podcasters.spotify.com/
2. Click **"Claim a podcast"** or **"Add a podcast"**
3. Paste your RSS URL: `https://yourusername.github.io/yourrepo/podcast.xml`
4. Fill in podcast details (title, description, cover art, etc.)
5. Submit

Spotify will validate and list your podcast within hours. New episodes will appear automatically when you re-run the generator.

## Step 6: (Optional) Submit to Apple Podcasts

1. Go to **Apple Podcasts Connect**: https://podcastsconnect.apple.com/
2. Click **"My Podcasts"** → **"Add a Show"**
3. Paste your RSS URL
4. Fill in details and submit

Apple will review your feed; typically approval takes 24–48 hours.

## Step 7: Schedule Daily Generation (Optional)

To run the generator automatically every day at 6 AM:

1. Open crontab:
   ```bash
   crontab -e
   ```

2. Add this line (replace paths as needed):
   ```cron
   0 6 * * * cd /home/labuser/podcast_ai && /home/labuser/podcast_ai/venv/bin/python3 src/main_runner.py >> /home/labuser/podcast_ai/automation.log 2>&1
   ```

3. Save and exit (`:wq` in vim)

The script will now run daily, generate a new episode, and publish it to GitHub — Spotify/Apple will pick it up within hours.

## Troubleshooting

**"GitHub upload failed"**
- Ensure `GITHUB_TOKEN` and `GITHUB_REPO` are correctly set in `.env`.
- Test the token: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user` — should show your GitHub username.

**RSS feed not updating**
- Ensure `podcast.xml` is in your repo root and GitHub Pages is enabled.
- Wait a few minutes for GitHub Pages to rebuild.

**Spotify/Apple not picking up episodes**
- Make sure the RSS URL is correct and publicly accessible.
- Test: `curl https://yourusername.github.io/yourrepo/podcast.xml` — should return valid XML.
- Re-submit the RSS URL in Spotify/Apple if it shows stale content.

## Next Steps

Once this is working:
- **Higher-quality audio**: Integrate Gemini TTS or ElevenLabs (see `ADVANCED_TTS.md` when ready).
- **Multi-voice discussion**: Generate structured Host+Guest conversations with Gemini (already implemented — just needs Gemini API key).
- **Custom scheduling**: Modify cron schedule or use a task scheduler for different frequencies.

Good luck! 🎙️
