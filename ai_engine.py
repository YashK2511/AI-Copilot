import requests
from prompts import PROMPT_MAP, COMPRESSION_PROMPT, HIGHLIGHT_PROMPT
import json
import time
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"
MAX_NOTES_CHARS = 3000  # ~500 words — 2 page limit


def _call_ollama(prompt: str, retries: int = 3) -> str:
    """
    POST to local Ollama API and return the model response text.
    Retries up to 3 times with exponential backoff.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.3,   # Lower temp = more consistent formatting
            "num_ctx": 8192       # Extended context window
        }
    }

    for attempt in range(retries):
        try:
            resp = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180)
            resp.raise_for_status()
            
            full_response = []
            sys.stdout.write("\n🤖 [Llama 3.1] Generating: ")
            sys.stdout.flush()
            
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    text = chunk.get("response", "")
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    full_response.append(text)
                    if chunk.get("done"):
                        break
            
            sys.stdout.write("\n\n")
            sys.stdout.flush()
            return "".join(full_response).strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure it's running: `ollama serve`"
            )
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError("Llama 3.1 took too long. Try a shorter video.")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Llama 3.1 error: {str(e)}")


def generate_notes(chunks: list, mode: str = "notes") -> str:
    """
    Generate structured output from transcript chunks.
    Modes: 'notes' | 'flashcards' | 'predict'
    """
    prompt_template = PROMPT_MAP.get(mode, PROMPT_MAP["notes"])
    all_output = []
    total = len(chunks)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n📦 [Chunk {i}/{total}] Processing chunk {i} of {total}...")
        prompt = prompt_template.format(transcript=chunk)
        result = _call_ollama(prompt)
        all_output.append(result)

    combined = "\n\n".join(all_output)

    # Phase 6: Compress if over 2-page limit (notes mode only)
    if mode == "notes" and len(combined) > MAX_NOTES_CHARS:
        print("\n✂️  [Compressing] Notes too long, running compression pass...")
        compress_prompt = COMPRESSION_PROMPT.format(notes=combined)
        combined = _call_ollama(compress_prompt)

    return combined



def extract_highlights(notes: str) -> list:
    """
    Phase 10: Extract top 5 must-memorize lines from generated notes.
    Returns a list of strings.
    """
    prompt = HIGHLIGHT_PROMPT.format(notes=notes)
    raw = _call_ollama(prompt)

    try:
        highlights = json.loads(raw)
        if isinstance(highlights, list):
            return highlights[:5]
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: return first 5 non-empty lines if JSON parse fails
    lines = [l.strip() for l in raw.split('\n') if l.strip()]
    return lines[:5]
