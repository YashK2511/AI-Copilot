from collections import Counter
import re


def predict_exam_questions(notes: str) -> list:
    """
    Detect repeated concepts in notes and tag HIGH/MEDIUM probability.
    Returns list of dicts: [{"concept": ..., "probability": ..., "question": ...}]
    """
    # Extract bolded terms (**term**)
    terms = re.findall(r'\*\*(.+?)\*\*', notes)
    # Also capture bullet point key terms (first 3 words of each bullet)
    bullets = re.findall(r'[•\-]\s+(.+)', notes)
    for bullet in bullets:
        first_words = ' '.join(bullet.split()[:3])
        terms.append(first_words)

    freq = Counter(terms)
    predictions = []

    for term, count in freq.most_common(12):
        if len(term.strip()) < 3:
            continue
        prob = "HIGH" if count >= 2 else "MEDIUM"
        predictions.append({
            "concept": term,
            "probability": prob,
            "question": f"Explain the concept of '{term}' and its significance."
        })

    return predictions[:8]  # Max 8 predictions
