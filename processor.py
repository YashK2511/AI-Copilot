import re


def clean_text(text: str) -> str:
    """Remove transcript artifacts and normalize whitespace."""
    text = re.sub(r'\[.*?\]', '', text)   # Remove [Music], [Applause], etc.
    text = re.sub(r'\(.*?\)', '', text)   # Remove (inaudible), (laughter), etc.
    text = re.sub(r'\s+', ' ', text)       # Collapse newlines / extra spaces
    return text.strip()


def chunk_text(text: str, max_chars: int = 8000) -> list:
    """
    Split text into safe chunks for Llama 3.1.
    Splits at sentence boundaries to avoid cutting mid-thought.
    8000 chars ≈ ~2000 tokens, well within default Ollama context.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    sentences = text.split('. ')

    for sentence in sentences:
        if len(current) + len(sentence) + 2 > max_chars:
            if current:
                chunks.append(current.strip())
            current = sentence + '. '
        else:
            current += sentence + '. '

    if current.strip():
        chunks.append(current.strip())

    return chunks


def compress_to_two_pages(notes: str, max_chars: int = 3000) -> tuple:
    """
    Check if notes exceed 2-page limit (~3000 chars / ~500 words).
    Returns (notes, needs_compression: bool)
    """
    if len(notes) <= max_chars:
        return notes, False
    return notes, True
