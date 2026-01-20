# Path: backend/rag_engine.py
# Purpose: RAG engine with strict document grounding

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    Document,
    PromptTemplate
)
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
import logging

from config import (
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoraRAGEngine:

    def __init__(self):
        logger.info("🚀 Initializing Lora RAG Engine")

        self.llm = Groq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=150  # Limit response length
        )

        self.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL
        )

        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = CHUNK_SIZE
        Settings.chunk_overlap = CHUNK_OVERLAP

        self.index = None
        self.query_engine = None
        self.indexed_files = set()

        self._initialize_index()

    def _initialize_index(self):
        try:
            if (STORAGE_DIR / "docstore.json").exists():
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(STORAGE_DIR)
                )
                self.index = load_index_from_storage(storage_context)
                self._update_indexed_files()
            else:
                self._create_new_index()
        except Exception:
            self._create_new_index()

        self._create_query_engine()

    def _load_txt_files(self):
        documents = []

        for txt_file in DOCUMENTS_DIR.glob("*.txt"):
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if text:
                documents.append(
                    Document(
                        text=text,
                        metadata={"file_name": txt_file.name}
                    )
                )

        return documents

    def _create_new_index(self):
        docs = self._load_txt_files()

        if docs:
            self.index = VectorStoreIndex.from_documents(docs)
        else:
            self.index = VectorStoreIndex([])

        self.index.storage_context.persist(
            persist_dir=str(STORAGE_DIR)
        )
        self._update_indexed_files()

    def _update_indexed_files(self):
        self.indexed_files = set(f.name for f in DOCUMENTS_DIR.glob("*.txt"))

    def _create_query_engine(self):
        # Custom concise prompt template
        qa_prompt = PromptTemplate(
            "Context:\n{context_str}\n\n"
            "Question: {query_str}\n\n"
            "Instructions: Answer in 2-3 sentences maximum. Be direct and concise.\n"
            "Answer:"
        )
        
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        # Update prompts
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt}
        )

    def query(self, full_prompt: str) -> dict:
        try:
            response = self.query_engine.query(full_prompt)

            # Don't include sources in the response
            return {
                "response": str(response),
                "sources": []
            }

        except Exception as e:
            logger.error(f"Query error: {e}")
            return {
                "response": "I encountered an error. Please contact customer care.",
                "sources": []
            }


_rag_engine = None


def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = LoraRAGEngine()
    return _rag_engine