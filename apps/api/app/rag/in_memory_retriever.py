import json
import os
import re
from typing import List, Optional, Any
from app.services.text_utils import clean_text_for_matching, strip_basmalah, extract_surah_name

class InMemoryRetriever:
    """
    In-memory exact search retriever for all sources (Quran, Hadith, Tafsir, etc).
    Loads `all_sources.json` at startup to bypass database I/O and SQL encoding issues.
    """
    def __init__(self):
        self.chunks = []
        self._load_data()

    def _skeletal(self, text: str) -> str:
        if not text:
            return ""
        # Remove spaces, Alef forms, Yaa forms, Waw, Hamza, and Quranic Maddah/symbols
        return re.sub(r"[اآأإىيؤئءو\s\u0653\u06E4\u06E5\u06E6]", "", text)

    def _load_data(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'all_sources.json')
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
            
        # Precompute cleaned and skeletal text for O(1) string matching without overhead
        for chunk in self.chunks:
            raw_normalized = chunk.get("text_normalized") or chunk.get("text") or ""
            # Strip basmalah only if it's quran (source_type == QURAN)
            if chunk.get("source_type") == "QURAN":
                raw_normalized = strip_basmalah(raw_normalized)
            cleaned = clean_text_for_matching(raw_normalized)
            chunk["_cleaned_text"] = cleaned
            if chunk.get("source_type") == "QURAN":
                chunk["_skeletal_text"] = self._skeletal(cleaned)

    def _to_retrieved_chunk(self, chunk: dict) -> Any:
        from app.rag.retrieval import RetrievedChunk
        return RetrievedChunk(
            chunk_id=chunk["chunk_id"],
            source_id=chunk["source_id"],
            source_code=chunk["source_code"],
            source_title=chunk["source_title"],
            source_title_ar=chunk.get("source_title_ar"),
            source_type=chunk["source_type"],
            author=chunk.get("author"),
            author_ar=chunk.get("author_ar"),
            edition=chunk.get("edition"),
            text=chunk["text"],
            text_normalized=chunk.get("text_normalized"),
            page=chunk.get("page"),
            chapter=chunk.get("chapter"),
            section=chunk.get("section"),
            hadith_number=chunk.get("hadith_number"),
            surah_number=chunk.get("surah_number"),
            verse_number=chunk.get("verse_number"),
            reference=chunk.get("reference"),
            grading=None,
            grading_authority=None,
            exact_match=True,
            final_score=1.0,
            retrieval_method="exact_in_memory"
        )

    def exact_search_quran(self, query_clean: str, surah_num: Optional[int] = None) -> List[Any]:
        """
        Perform an exact substring search over the entire Quran.
        If surah_num is provided, restricts search to that surah.
        """
        if not self.chunks or not query_clean or len(query_clean) < 5:
            return []

        results = []
        query_skel = self._skeletal(query_clean)

        for chunk in self.chunks:
            if chunk.get("source_type") != "QURAN":
                continue
            if surah_num and chunk.get("surah_number") != surah_num:
                continue
                
            chunk_clean = chunk["_cleaned_text"]
            chunk_skel = chunk.get("_skeletal_text", "")
            
            # Match strictly first, then fallback to skeletal
            if chunk_clean and (chunk_clean in query_clean or query_clean in chunk_clean):
                results.append(self._to_retrieved_chunk(chunk))
            elif chunk_skel:
                # To prevent short Huroof Muqatta'ah like 'حم' or 'يس' from falsely matching inside a long query,
                # we enforce a minimum length for chunk_skel if it is inside query_skel
                if query_skel in chunk_skel:
                    results.append(self._to_retrieved_chunk(chunk))
                elif chunk_skel in query_skel and len(chunk_skel) > 10:
                    results.append(self._to_retrieved_chunk(chunk))
                
        return results

    def exact_search_general(self, query_clean: str, claim_type: str = "hadith") -> List[Any]:
        """
        Perform an exact substring search over Hadith, Tafsir, or other general sources.
        """
        if not self.chunks or not query_clean or len(query_clean) < 5:
            return []

        source_type_filter = None
        if claim_type == "hadith":
            source_type_filter = "HADITH"
        elif claim_type == "tafsir":
            source_type_filter = "TAFSIR"
        elif claim_type in ["fiqh", "scholarly"]:
            source_type_filter = "SCHOLARLY"

        results = []
        for chunk in self.chunks:
            # Filter by source_type if applicable
            if source_type_filter and chunk.get("source_type") != source_type_filter:
                # Also include FIQH in SCHOLARLY and vice versa just in case
                if source_type_filter == "SCHOLARLY" and chunk.get("source_type") == "FIQH":
                    pass
                else:
                    continue
                
            chunk_clean = chunk["_cleaned_text"]
            # For general text, we look for query in chunk or chunk in query
            if chunk_clean and (chunk_clean in query_clean or query_clean in chunk_clean):
                results.append(self._to_retrieved_chunk(chunk))
                
        return results

# Singleton instance
in_memory_retriever = InMemoryRetriever()
