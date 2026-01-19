# Path: backend/answer_verifier.py
# Purpose:
# - Verify KB (Excel) answer against user question
# - Use LLM ONLY to check relevance & lightly rephrase
# - NEVER add new facts
# - NEVER invent answers
# - If answer is NOT relevant → return None (forces TXT-RAG fallback)

from llama_index.llms.groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL

llm = Groq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0.0  # strict, no creativity
)


def verify_answer(user_question: str, kb_answer: str) -> str | None:
    """
    Returns:
      - refined answer (string) if KB answer is relevant & correct
      - None if KB answer should NOT be used
    """

    prompt = f"""
You are a strict financial QA validator.

User question:
{user_question}

Cached answer:
{kb_answer}

TASK:
1. Decide if the cached answer DIRECTLY answers the user question.
2. If it does NOT clearly answer the question, respond ONLY with:
   INVALID
3. If it DOES answer correctly:
   - Keep the same meaning
   - Do NOT add new facts
   - Do NOT change numbers, percentages, conditions
   - You may lightly rephrase for clarity (optional)
   - Be concise and human-like

IMPORTANT:
- Never guess
- Never combine multiple topics
- Never expand scope
"""

    result = llm.complete(prompt)
    text = str(result).strip()

    if text.upper().startswith("INVALID"):
        return None

    return text
