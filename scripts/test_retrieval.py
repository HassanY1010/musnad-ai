"""
Quick test to verify the retrieval pipeline works end-to-end.
Run from the apps/api directory.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./apps/api/musnad_ai.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

TEST_CLAIMS = [
    # Hadith - full with attribution
    "قال رسول الله صلى الله عليه وسلم: إنما الأعمال بالنيات",
    # Hadith - core matn only
    "إنما الأعمال بالنيات",
    # Quran verse
    "إن الله لا يظلم مثقال ذرة",
    # Another hadith
    "الدين النصيحة",
]

async def main():
    from app.rag.retrieval import HybridRetriever
    from app.services.text_utils import normalize_arabic

    retriever = HybridRetriever()

    async with AsyncSessionLocal() as db:
        for claim in TEST_CLAIMS:
            print(f"\n{'='*60}")
            print(f"CLAIM: {claim[:80]}")
            normalized = normalize_arabic(claim)
            result = await retriever.retrieve(db, claim, "hadith", normalized_claim=normalized)
            print(f"  exact_matches : {result.exact_matches_found}")
            print(f"  total_retrieved: {result.total_retrieved}")
            for i, chunk in enumerate(result.chunks[:3]):
                print(f"  [{i+1}] method={chunk.retrieval_method} score={chunk.final_score:.3f}")
                print(f"       source={chunk.source_code}  hadith#={chunk.hadith_number}")
                print(f"       text  ={chunk.text[:80]}...")

if __name__ == "__main__":
    asyncio.run(main())
