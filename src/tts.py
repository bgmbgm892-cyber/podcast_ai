"""Simple TTS synthesizer using gTTS and pydub as a fallback implementation.

This is a basic, offline-friendly implementation intended as a fallback for
development. For production multi-voice or higher-quality output, integrate
with a cloud TTS provider (Gemini TTS, ElevenLabs, etc.).
"""
import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment, effects
from utils import timestamp


def script_to_segments(script_text):
    """Split the script into short segments to synthesize.

    This naive splitter groups text by blank lines and by speaker markers
    (lines starting with 'Host:' or 'Guest:').
    Returns a list of strings.
    """
    lines = [ln.strip() for ln in script_text.splitlines()]
    segments = []
    cur = []
    for ln in lines:
        if not ln:
            if cur:
                segments.append(' '.join(cur))
                cur = []
            continue
        # treat speaker-labeled lines as boundaries
        if ln.startswith('Host:') or ln.startswith('Guest:'):
            if cur:
                segments.append(' '.join(cur))
            segments.append(ln)
            cur = []
            continue
        cur.append(ln)
    if cur:
        segments.append(' '.join(cur))
    return segments


def synthesize(script_text, out_path=None, lang='en'):
    """Synthesize script_text into a single MP3 file.

    - Uses `gTTS` to produce short MP3s for each segment, then stitches
      them together with `pydub`.
    - `out_path` if provided is used; otherwise a timestamped file in
      `episodes/` is created.
    """
    segments = script_to_segments(script_text)
    if not segments:
        raise ValueError('Empty script_text')

    parts = []
    silence = AudioSegment.silent(duration=300)  # 300ms gap

    for i, seg in enumerate(segments):
        # Use gTTS to generate the audio for this segment
        # Retry up to 3 times for network resilience
        max_retries = 3
        for attempt in range(max_retries):
            try:
                tts = gTTS(text=seg, lang=lang)
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tf:
                    tmp_name = tf.name
                tts.save(tmp_name)
                part = AudioSegment.from_file(tmp_name, format='mp3')
                try:
                    os.remove(tmp_name)
                except Exception:
                    pass
                break  # Success, exit retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    print(f'TTS segment {i} attempt {attempt+1} failed, retrying in 2s...')
                    time.sleep(2)
                else:
                    print(f'TTS segment {i} failed after {max_retries} attempts: {e}')
                    raise

        parts.append(part)
        parts.append(silence)

    # concatenate
    final = parts[0]
    for p in parts[1:]:
        final = final + p

    # normalize for consistent loudness
    final = effects.normalize(final)

    if not out_path:
        os.makedirs('episodes', exist_ok=True)
        out_path = f"episodes/episode_{timestamp()}.mp3"

    final.export(out_path, format='mp3')
    return out_path


if __name__ == '__main__':
    print('tts module loaded')