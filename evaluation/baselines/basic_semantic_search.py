"""
MUSNAD AI - Baseline B: Basic Semantic Search (Dense Vector Only)
Simulates standard vector-only RAG without deterministic verification rules,
without exact canonical overrides, without fiqh specialist referral, and without scholarly review routing.
"""
from typing import List, Dict, Any, Optional


class BasicSemanticSearchBaseline:
    """
    Baseline B: Basic Semantic Retrieval
    - Uses dense vector similarity alone to determine support.
    - If top cosine score >= 0.70: claims 'supported'.
    - If top cosine score is 0.45-0.70: claims 'partially_supported'.
    - If top cosine score < 0.45 or no results: claims 'insufficient_evidence'.
    - Lacks exact match guarantees, fiqh referral logic, and attribution caution.
    """

    def __init__(self, high_threshold: float = 0.70, medium_threshold: float = 0.45):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def evaluate_claim(self, claim_text: str, retrieved_chunks: List[Any]) -> Dict[str, Any]:
        if not retrieved_chunks:
            return {
                "status": "insufficient_evidence",
                "top_score": 0.0,
                "retrieved_count": 0,
                "explanation": "No chunks found above minimum similarity threshold.",
            }

        top_score = max((getattr(c, "final_score", 0.0) for c in retrieved_chunks), default=0.0)

        if top_score >= self.high_threshold:
            return {
                "status": "supported",
                "top_score": round(top_score, 4),
                "retrieved_count": len(retrieved_chunks),
                "explanation": f"Top semantic similarity score ({top_score:.2f}) meets support threshold.",
            }
        elif top_score >= self.medium_threshold:
            return {
                "status": "partially_supported",
                "top_score": round(top_score, 4),
                "retrieved_count": len(retrieved_chunks),
                "explanation": f"Top semantic similarity score ({top_score:.2f}) meets partial support threshold.",
            }
        else:
            return {
                "status": "insufficient_evidence",
                "top_score": round(top_score, 4),
                "retrieved_count": len(retrieved_chunks),
                "explanation": f"Top semantic similarity score ({top_score:.2f}) below relevance threshold.",
            }
