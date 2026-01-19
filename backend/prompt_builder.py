# Path: backend/prompt_builder.py
# Purpose: Human-like, concise, context-aware prompt builder

from typing import List, Tuple

def build_prompt(
    system_prompt: str,
    chat_history: List[Tuple[str, str]],
    user_question: str
) -> str:

    history_text = ""
    for role, content in chat_history:
        prefix = "User" if role == "user" else "Assistant"
        history_text += f"{prefix}: {content}\n"

    return f"""
{system_prompt}

Conversation history (use ONLY to understand context, not as facts):
{history_text}

RESPONSE GUIDELINES:
- Keep answers short (1–4 lines).
- Be natural and human-like.
- Do NOT sound like a fixed template.
- Do NOT list raw values unless appropriate.
- Phrase answers so they feel conversational.
- Example:
  ❌ "Gold loan interest rate is 9%."
  ✅ "The interest rate for a gold loan starts from 9% per annum."

- If the user asks a vague question, ask ONE clarification.
- Otherwise, answer directly.

User Question:
{user_question}
"""
