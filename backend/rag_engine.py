# Path: backend/rag_engine.py
# Purpose:
# - TXT files are PRIMARY source of truth
# - Strict document grounding
# - NO file names leaked to UI
# - Stable, low-token, deterministic behavior

from pathlib import Path
import logging

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    Document
)
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DOCUMENTS_DIR,
    STORAGE_DIR,
    SYSTEM_PROMPT,
    MAX_TOKENS
)


# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoraRAGEngine:
    """
    RAG engine where:
    - TXT documents are authoritative
    - LLM is constrained (no hallucination)
    - UI sees friendly source label only
    """

    def __init__(self):
        logger.info("🚀 Initializing Lora RAG Engine")

        # LLM (strict, low creativity)
        self.llm = Groq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            max_retries=1,          # prevent token explosion
        )

        # Embeddings
        self.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL
        )

        # Global LlamaIndex settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = CHUNK_SIZE
        Settings.chunk_overlap = CHUNK_OVERLAP

        self.index = None
        self.query_engine = None

        self._initialize_index()

    # -------------------------------------------------
    # Index initialization
    # -------------------------------------------------
    def _initialize_index(self):
        try:
            if (STORAGE_DIR / "docstore.json").exists():
                logger.info("📦 Loading existing index from storage")
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(STORAGE_DIR)
                )
                self.index = load_index_from_storage(storage_context)
            else:
                logger.info("📄 Creating new index from TXT documents")
                self._create_new_index()
        except Exception as e:
            logger.warning("⚠️ Index load failed, rebuilding index")
            logger.error(e)
            self._create_new_index()

        self._create_query_engine()

    # -------------------------------------------------
    # TXT loading
    # -------------------------------------------------
    def _load_txt_files(self):
        documents = []

        for txt_file in DOCUMENTS_DIR.glob("*.txt"):
            try:
                text = txt_file.read_text(encoding="utf-8").strip()
            except Exception:
                continue

            if text:
                documents.append(
                    Document(
                        text=text,
                        metadata={
                            # metadata kept internally only
                            "source": "lora_finance_docs"
                        }
                    )
                )

        return documents

    # -------------------------------------------------
    # Index creation
    # -------------------------------------------------
    def _create_new_index(self):
        docs = self._load_txt_files()

        if docs:
            self.index = VectorStoreIndex.from_documents(docs)
        else:
            logger.warning("⚠️ No TXT documents found, creating empty index")
            self.index = VectorStoreIndex([])

        self.index.storage_context.persist(
            persist_dir=str(STORAGE_DIR)
        )

    # -------------------------------------------------
    # Query engine
    # -------------------------------------------------
    def _create_query_engine(self):
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )

    # -------------------------------------------------
    # Public query
    # -------------------------------------------------
    def query(self, full_prompt: str) -> dict:
        """
        full_prompt already contains:
        - system rules
        - full current-session context
        - user question
        """
        try:
            response = self.query_engine.query(full_prompt)

            return {
                "response": str(response),
                # Friendly, non-technical source label only
                "sources": ["Lora Finance Company Policies and Documents"]
            }

        except Exception as e:
            logger.error("❌ RAG query failed")
            logger.error(e)
            return {
                "response": "I encountered an error while retrieving information. Please contact customer care.",
                "sources": []
            }


# -------------------------------------------------
# Singleton accessor
# -------------------------------------------------
_rag_engine = None


def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = LoraRAGEngine()
    return _rag_engine
