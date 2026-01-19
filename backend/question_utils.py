# Path: backend/question_utils.py
# Purpose:
# - Decide whether a question is SAFE for Excel KB lookup
# - Block vague / half / context-dependent questions
# - TXT-RAG + LLM handles blocked questions

def is_vague_question(question: str) -> bool:
    q = question.lower().strip()

    # Very short questions are vague
    if len(q.split()) <= 2:
        return True

    vague_tokens = {
        "documents",
        "eligibility",
        "criteria",
        "rate",
        "interest",
        "repayment",
        "charges",
        "fees",
    }

    if q in vague_tokens:
        return True

    return False


def is_safe_for_kb(question: str) -> bool:
    """
    KB-safe ONLY if:
    - Full standalone question
    - Explicit loan type present
    - Not vague
    """

    if is_vague_question(question):
        return False

    loan_keywords = [
        "gold loan",
        "personal loan",
        "business loan",
        "home loan",
        "education loan",
    ]

    q = question.lower()

    if not any(k in q for k in loan_keywords):
        return False

    return True
