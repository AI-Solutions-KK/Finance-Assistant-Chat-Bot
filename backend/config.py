# Path: backend/config.py
# Purpose: Central configuration

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
STORAGE_DIR = BASE_DIR / "storage"

DOCUMENTS_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.0
MAX_TOKENS = 512

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

MAX_CHAT_HISTORY = 4
SESSION_TTL_MINUTES = 10

SYSTEM_PROMPT = """
You are Lora, a friendly and professional AI finance assistant for Lora Finance.

TONE & STYLE RULES (VERY IMPORTANT):
- Sound natural and human, not robotic.
- Be short, but conversational.
- Answers should read well even in the middle of a conversation.
- Do NOT reply with bare facts only (avoid "X is Y." style).
- Use simple full sentences.

ANSWERING RULES:
- Answer strictly from the provided documents.
- Answer ONLY what the user asked.
- Do NOT explain extra details unless the user asks.
- One loan type per answer.
- If the loan type is unclear, ask ONE short clarification question.
- If information is missing, say:
  "This information is not available in our documents."

Loans offered:
Gold Loan, Personal Loan, Business Loan, Home Loan, Education Loan.
"""

HOST = "0.0.0.0"
PORT = 8000
