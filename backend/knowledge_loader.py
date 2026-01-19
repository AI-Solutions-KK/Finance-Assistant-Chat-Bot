# Path: backend/knowledge_loader.py
# Purpose:
# - Load Excel Q&A as OPTIONAL cache (token saving only)
# - Perform SAFE semantic match
# - Do NOT force match on vague / half questions
# - TXT RAG remains primary knowledge source

import pandas as pd
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

from backend.config import KNOWLEDGE_XLSX

# Lightweight, stable embedding model
_EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


class KnowledgeBox:
    def __init__(self):
        if not KNOWLEDGE_XLSX.exists():
            self.enabled = False
            return

        self.enabled = True
        self.df = pd.read_excel(KNOWLEDGE_XLSX, sheet_name="qa")

        # REQUIRED columns: question, answer
        self.questions = self.df["question"].astype(str).tolist()
        self.answers = self.df["answer"].astype(str).tolist()

        # Pre-compute embeddings once (startup only)
        self.embeddings = _EMBED_MODEL.encode(
            self.questions,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

    def _is_vague(self, question: str) -> bool:
        """
        Block vague / half questions from KB lookup.
        These MUST go to TXT RAG + LLM.
        """
        q = question.lower().strip()
        vague_tokens = {
            "documents", "eligibility", "criteria",
            "rate", "interest", "repayment", "charges", "fees"
        }

        if len(q.split()) <= 2:
            return True

        if q in vague_tokens:
            return True

        return False

    def search(self, user_question: str, threshold: float = 0.80):
        """
        Returns:
          - dict {answer, score} if SAFE match found
          - None if no safe KB match
        """

        if not self.enabled:
            return None

        # 🚫 Do not even try KB for vague questions
        if self._is_vague(user_question):
            return None

        query_emb = _EMBED_MODEL.encode(
            user_question,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        scores = util.cos_sim(query_emb, self.embeddings)[0]

        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        if best_score >= threshold:
            return {
                "answer": self.answers[best_idx],
                "score": best_score
            }

        return None


# Singleton loader
_knowledge_box = None


def get_knowledge_box():
    global _knowledge_box
    if _knowledge_box is None:
        _knowledge_box = KnowledgeBox()
    return _knowledge_box
