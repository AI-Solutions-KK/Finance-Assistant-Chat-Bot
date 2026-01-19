# Path: backend/main.py
# Purpose: FastAPI server with intent-aware context, short answers,
#          and auto session cleanup (NO UI changes)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import get_rag_engine
from session_store import (
    init_db,
    create_session_if_not_exists,
    save_message,
    get_recent_messages,
    delete_expired_sessions,
    get_last_loan_type,
    set_last_loan_type
)
from prompt_builder import build_prompt
from config import SYSTEM_PROMPT, HOST, PORT, MAX_CHAT_HISTORY, SESSION_TTL_MINUTES

# -------------------------------------------------
# App setup
# -------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
rag_engine = get_rag_engine()


# -------------------------------------------------
# Request model
# -------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str


# -------------------------------------------------
# Intent helpers
# -------------------------------------------------
LOAN_KEYWORDS = {
    "gold loan": "gold loan",
    "personal loan": "personal loan",
    "business loan": "business loan",
    "home loan": "home loan",
    "education loan": "education loan"
}

SHORT_FOLLOWUPS = {
    "documents", "documents?",
    "eligibility", "eligibility?",
    "repayment", "repayment?",
    "interest", "interest?",
    "interest rate", "rate", "rate?"
}


def detect_loan_type(text: str):
    text = text.lower()
    for key, value in LOAN_KEYWORDS.items():
        if key in text:
            return value
    return None


# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------------------------------
# Chat endpoint
# -------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    # 🔄 Auto cleanup expired sessions
    delete_expired_sessions(
        older_than_minutes=SESSION_TTL_MINUTES
    )

    session_id = req.session_id
    user_message = req.message.strip()

    create_session_if_not_exists(session_id)
    save_message(session_id, "user", user_message)

    # ---------------------------------------------
    # Intent tracking (CORE FIX)
    # ---------------------------------------------
    explicit_loan = detect_loan_type(user_message)

    if explicit_loan:
        # User explicitly mentioned a loan → lock intent
        set_last_loan_type(session_id, explicit_loan)
        active_loan = explicit_loan
    else:
        # Use previous intent if available
        active_loan = get_last_loan_type(session_id)

    # ---------------------------------------------
    # Handle short follow-up questions correctly
    # ---------------------------------------------
    normalized = user_message.lower().strip()

    if normalized in SHORT_FOLLOWUPS:
        if active_loan:
            # Rewrite internally to preserve context
            user_message = f"{normalized} for {active_loan}"
        else:
            # No context → ask clarification
            return {
                "response": "Which loan are you referring to?",
                "sources": []
            }

    # ---------------------------------------------
    # Build prompt with limited history
    # ---------------------------------------------
    history = get_recent_messages(
        session_id,
        limit=MAX_CHAT_HISTORY
    )

    full_prompt = build_prompt(
        SYSTEM_PROMPT,
        history,
        user_message
    )

    # ---------------------------------------------
    # RAG query
    # ---------------------------------------------
    result = rag_engine.query(full_prompt)

    save_message(session_id, "assistant", result["response"])

    return {
        "response": result["response"],
        "sources": result.get("sources", [])
    }


# -------------------------------------------------
# Run server
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
