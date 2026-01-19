# Path: backend/main.py
# Purpose:
# - Excel knowledge box first
# - RAG fallback
# - Stateless (NO session memory)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Fixed: Use relative imports for package resolution
from .knowledge_loader import get_knowledge_box
from .answer_verifier import verify_answer
from .rag_engine import get_rag_engine
from .prompt_builder import build_prompt
from .config import SYSTEM_PROMPT, HOST, PORT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

kb = get_knowledge_box()
rag_engine = get_rag_engine()


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    user_question = req.message.strip()

    # 1️⃣ Knowledge Box (Excel)
    kb_match = kb.search(user_question)

    if kb_match:
        verified = verify_answer(
            user_question,
            kb_match["answer"]
        )
        # Fixed: Only return if verification succeeded; else fallback to RAG
        if verified:
            return {
                "response": verified,
                "sources": ["Lora Finance Company Policies and Documents"]
            }

    # 2️⃣ RAG fallback (Runs if KB search fails OR verification returns None)
    prompt = build_prompt(
        SYSTEM_PROMPT,
        [],
        user_question
    )

    result = rag_engine.query(prompt)

    return {
        "response": result["response"],
        "sources": ["Lora Finance Company Policies and Documents"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)