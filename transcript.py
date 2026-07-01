from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
import re
import whisper
import subprocess
import os
from functools import lru_cache


def extract_video_id(url: str) -> str:
    """Supports youtube.com/watch?v=, youtu.be/, and /shorts/ URL formats."""
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"/shorts/([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL. Please use a standard youtube.com or youtu.be link.")


def transcribe_with_whisper(video_id: str) -> str:
    """Fallback: Download audio via yt-dlp and transcribe using local Whisper."""
    audio_file = f"/tmp/{video_id}.mp3"
    print(f"No captions found. Falling back to Whisper for {video_id}...")
    
    # Download audio
    subprocess.run([
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", audio_file,
        f"https://www.youtube.com/watch?v={video_id}"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Transcribe (using 'base' model for speed on CPU/MPS)
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    
    # Cleanup
    if os.path.exists(audio_file):
        os.remove(audio_file)
        
    return result["text"].strip()


@lru_cache(maxsize=10)
def get_transcript(url: str) -> str:
    """Fetch transcript text from a YouTube video URL."""
    video_id = extract_video_id(url)
    try:
        api = YouTubeTranscriptApi()
        entries = api.fetch(video_id)
        return " ".join(entry.text for entry in entries)
    except TranscriptsDisabled:
        # Fallback to local Whisper
        return transcribe_with_whisper(video_id)
    except VideoUnavailable:
        raise RuntimeError("This video is private or unavailable.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript: {str(e)}")
