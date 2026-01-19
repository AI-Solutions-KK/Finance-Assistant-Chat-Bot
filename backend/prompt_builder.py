# Path: backend/prompt_builder.py
# Purpose: Balanced context-aware prompt builder
# Design:
# - Ask clarification ONLY when loan type is unclear
# - NEVER over-interrogate the user
# - Assume sensible defaults for sub-types (offers, variants)
# - Mention variants AFTER answering, not before

from typing import List, Tuple


HIGH_LEVEL_AMBIGUOUS = {
    "interest",
    "interest rate",
    "rates",
    "eligibility",
    "repayment",
    "documents",
    "tenure",
    "duration",
    "amount"
}


def _is_high_level_ambiguous(question: str) -> bool:
    q = question.lower().strip()
    return q in HIGH_LEVEL_AMBIGUOUS or len(q.split()) <= 2


def build_prompt(
    system_prompt: str,
    chat_history: List[Tuple[str, str]],
    user_question: str
) -> str:

    history_text = ""
    for role, content in chat_history:
        prefix = "User" if role == "user" else "Assistant"
        history_text += f"{prefix}: {content}\n"

    ambiguity_rules = """
DISAMBIGUATION POLICY (VERY IMPORTANT):

1. Ask a clarification question ONLY if:
   - The loan type itself is unclear (gold, personal, home, business).

2. If the loan type IS clear:
   - DO NOT ask further clarification questions.
   - Assume the GENERAL / STANDARD option by default.
   - Answer first.
   - Mention special offers or variants AFTER the answer, if relevant.

3. NEVER ask multiple clarification questions in a row.

4. NEVER block the user from getting an answer once intent is reasonably clear.
"""

    answer_rules = """
ANSWERING RULES:

- Answer strictly from provided documents.
- Answer for ONLY ONE loan type at a time.
- Do NOT merge multiple loan types.
- Be concise and user-friendly.
- If an offer or variant exists, mention it briefly after answering.
"""

    return f"""
{system_prompt}

Conversation history (for intent understanding only):
{history_text}

{ambiguity_rules}

{answer_rules}

User Question:
{user_question}

IMPORTANT:
- If clarification is required, ask ONE short clarification question.
- Otherwise, provide the answer directly.
"""
