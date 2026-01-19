# Path: backend/main.py
# Purpose: FastAPI server with session-wise memory

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import get_rag_engine
from session_store import (
    init_db,
    create_session_if_not_exists,
    save_message,
    get_recent_messages
)
from prompt_builder import build_prompt
from config import SYSTEM_PROMPT, HOST, PORT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
rag_engine = get_rag_engine()


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id
    user_message = req.message

    create_session_if_not_exists(session_id)
    save_message(session_id, "user", user_message)

    history = get_recent_messages(session_id)

    full_prompt = build_prompt(
        SYSTEM_PROMPT,
        history,
        user_message
    )

    result = rag_engine.query(full_prompt)

    save_message(session_id, "assistant", result["response"])

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
