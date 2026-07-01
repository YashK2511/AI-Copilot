# ============================================================
#  PROMPTS — All LLM prompts live here for easy iteration
# ============================================================

# ------ EXAM NOTES (Default Mode) ------
NOTES_PROMPT = """
You are an expert academic tutor. Using the lecture transcript below,
generate structured, exam-ready study notes in EXACTLY this format.
No deviation. No preamble. No "Sure!" No extra commentary.

---
📘 **[Topic Title]**

**Definition:**
[1-2 sentence clear definition of the core concept]

**Key Points:**
• [Point 1]
• [Point 2]
• [Point 3]
• [Point 4]

**Short Answer (2-3 lines):**
[A concise paragraph a student would write in an exam]

**Possible Exam Questions:**
1. [Question 1]
2. [Question 2]
3. [Question 3]
---

STRICT RULES:
- Total output must fit in 2 printed pages (max 500 words).
- Do NOT add text outside the format above.
- If transcript covers multiple distinct topics, repeat the block per topic.
- Use student-friendly language. Define jargon when used.

TRANSCRIPT:
{transcript}
"""

# ------ FLASHCARDS ------
FLASHCARD_PROMPT = """
You are a flashcard generator. From the transcript below, generate study flashcards.

Each flashcard format:
Q: [Question]
A: [Answer — 1-2 sentences max]

Generate 8-12 flashcards covering the key concepts.
Output ONLY the flashcards. No preamble. No extra text.

TRANSCRIPT:
{transcript}
"""

# ------ EXAM PREDICTION ------
EXAM_PREDICT_PROMPT = """
You are an expert exam predictor. Analyze this transcript and predict the most
likely exam questions a teacher would ask. Tag each with probability:

[HIGH] — core definitions, repeated concepts, fundamental ideas
[MEDIUM] — applications, comparisons, secondary ideas

Format:
[HIGH] [Question]
[MEDIUM] [Question]

Generate exactly 5 HIGH and 3 MEDIUM questions.
Output ONLY the questions with tags. No extra text.

TRANSCRIPT:
{transcript}
"""

# ------ COMPRESSION (2-page enforcer) ------
COMPRESSION_PROMPT = """
The following study notes are too long. Compress them to fit in 2 printed pages
(max 500 words) while:
- Keeping ALL key points and definitions
- Keeping ALL exam questions
- Preserving the EXACT same format

NOTES:
{notes}
"""

# ------ HIGHLIGHT IMPORTANT LINES ------
HIGHLIGHT_PROMPT = """
From the study notes below, extract the 5 most important lines a student MUST memorize.
These should be the single most testable facts or definitions.

Return ONLY a JSON array of 5 strings, like:
["line1", "line2", "line3", "line4", "line5"]

No explanation. No preamble. Only the JSON array.

NOTES:
{notes}
"""

# ------ MODE → PROMPT MAPPING ------
PROMPT_MAP = {
    "notes": NOTES_PROMPT,
    "flashcards": FLASHCARD_PROMPT,
    "predict": EXAM_PREDICT_PROMPT,
}
