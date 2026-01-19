# Path: backend/prompt_builder.py
# Purpose:
# - Build prompt using FULL current-session chat for understanding
# - Chat history is CONTEXT ONLY (never knowledge)
# - Human, short, policy-aligned answers

def build_prompt(system_prompt: str, chat_history: list, user_question: str) -> str:
    history_text = ""

    for role, content in chat_history:
        prefix = "User" if role == "user" else "Assistant"
        history_text += f"{prefix}: {content}\n"

    return f"""
{system_prompt}

IMPORTANT:
- Conversation history is provided ONLY to understand intent and follow-ups.
- Do NOT treat previous answers as facts or sources.
- Answer strictly from the provided documents.
- Do NOT repeat old answers unless relevant to the current question.

Conversation history (context only):
{history_text}

User question:
{user_question}
"""
