from flask import Flask, render_template, request, jsonify
from transcript import get_transcript
from processor import clean_text, chunk_text
from ai_engine import generate_notes, extract_highlights
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Simple in-memory cache: key = (url, mode), value = response dict
_result_cache = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received.", "notes": None}), 400

    url = data.get("url", "").strip()
    mode = data.get("mode", "notes")  # "notes" | "flashcards" | "predict"

    if not url:
        return jsonify({"error": "No URL provided.", "notes": None}), 400

    # Bonus: Return cached result immediately for same URL+mode
    cache_key = (url, mode)
    if cache_key in _result_cache:
        print(f"[Cache] Returning cached result for {cache_key}")
        return jsonify(_result_cache[cache_key])

    try:
        # Step 1: Get transcript (cached in transcript.py via lru_cache)
        raw = get_transcript(url)
        transcript_preview = raw[:500].strip()  # First 500 chars for preview

        # Step 2: Clean and chunk
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)
        chunk_count = len(chunks)

        # Step 3: Generate with Llama 3.1
        notes = generate_notes(chunks, mode=mode)

        # Phase 10: Extract highlights in notes mode
        highlights = []
        if mode == "notes":
            try:
                highlights = extract_highlights(notes)
            except Exception:
                highlights = []  # Don't let highlight extraction crash the response

        result = {
            "notes": notes,
            "highlights": highlights,
            "transcript_preview": transcript_preview,
            "chunk_count": chunk_count,
            "error": None
        }

        # Store in cache
        _result_cache[cache_key] = result

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e), "notes": None}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e), "notes": None}), 422
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}", "notes": None}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)

