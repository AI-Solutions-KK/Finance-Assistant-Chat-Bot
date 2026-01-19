# Path: backend/config.py
# Purpose: Central configuration (TXT files are PRIMARY knowledge,
#          Excel is OPTIONAL cache only, session memory allowed)

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# Base paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = BASE_DIR / "documents"      # ✅ PRIMARY knowledge (TXT)
STORAGE_DIR = BASE_DIR / "storage"          # runtime (vectors, sessions)
KNOWLEDGE_XLSX = BASE_DIR / "knowledge" / "knowledge.xlsx"  # 🟡 OPTIONAL cache

DOCUMENTS_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)
KNOWLEDGE_XLSX.parent.mkdir(exist_ok=True)

# -------------------------------------------------
# LLM (Groq)
# -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment")

GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.0
MAX_TOKENS = 512

# -------------------------------------------------
# Embeddings (for TXT RAG + optional KB semantic match)
# -------------------------------------------------
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# -------------------------------------------------
# Session memory (TEMPORARY ONLY)
# - used for understanding context
# - cleared on refresh / close / TTL
# -------------------------------------------------
MAX_CHAT_HISTORY = 20        # full current session allowed
SESSION_TTL_MINUTES = 10     # auto-clean after idle

# -------------------------------------------------
# System prompt (FINAL, aligned with your rules)
# -------------------------------------------------
SYSTEM_PROMPT = """
You are Lora, a friendly and professional AI finance assistant for Lora Finance.

TONE & STYLE:
- Sound natural and human.
- Short, clear, conversational answers.
- Suitable even mid-conversation.
- Avoid robotic or bullet-only replies.

KNOWLEDGE RULES:
- TXT documents are the PRIMARY source of truth.
- Excel Q&A (if used) is only a cache to save tokens.
- Never treat user chat as knowledge.
- Never reuse past answers as facts.

ANSWERING RULES:
- Answer ONLY what is asked.
- One loan type per answer.
- If loan type is unclear, ask ONE short clarification question.
- If information is missing, say:
  "This information is not available in our documents."

Loans offered:
Gold Loan, Personal Loan, Business Loan, Home Loan, Education Loan.
"""

# -------------------------------------------------
# Server
# -------------------------------------------------
HOST = "0.0.0.0"
PORT = 8000
