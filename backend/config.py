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
    raise ValueError("GROQ_API_KEY not found in .env file")

GROQ_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.7
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# NEW: Context Awareness Settings
MEMORY_TOKEN_LIMIT = 4000  # Size of the context window
MAX_TOKENS = 1024
SYSTEM_PROMPT = """You are Lora, an AI finance assistant for Lora Finance company. 

CRITICAL INSTRUCTIONS:
1. Answer ONLY using information from the provided document context and chat history.
2. If information is not in the documents, say: "I don't have that specific information in our documents. Please contact our customer care at 1800-123-5678"
3. NEVER make up or hallucinate information
4. Be friendly, professional, and concise
5. Always cite sources when available

About Lora Finance:
We provide gold loans, personal loans, business loans, home loans, vehicle loans, and education loans with competitive rates."""

WATCH_INTERVAL = 2
HOST = "0.0.0.0"
PORT = 8000