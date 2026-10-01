import sys
import os
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

sys.path.append('E:/basira/musnad-ai/apps/api')
from app.rag.in_memory_retriever import in_memory_retriever

def run_test():
    print("Loading data into memory...")
    # It auto-loads on init, but we can access chunks directly.
    chunks = in_memory_retriever.chunks
    print(f"Total chunks in memory: {len(chunks)}\n")
    
    # Group by source_title
    sources_summary = defaultdict(int)
    examples = {}
    
    for c in chunks:
        title = c.get('source_title', 'Unknown Source')
        sources_summary[title] += 1
        
        # Save one example for each source
        if title not in examples:
            examples[title] = c
            
    print("="*50)
    print("📊 SOURCES SUMMARY")
    print("="*50)
    for title, count in sorted(sources_summary.items(), key=lambda x: x[1], reverse=True):
        print(f"✅ {title}: {count:,} texts")
        
    print("\n" + "="*50)
    print("🔎 ONE RANDOM EXAMPLE FROM EACH SOURCE")
    print("="*50)
    
    for title, chunk in examples.items():
        ref = chunk.get('reference') or chunk.get('hadith_number') or chunk.get('verse_number')
        text = chunk.get('text', '')[:100].replace('\n', ' ')
        print(f"\n📘 المصدر: {title}")
        print(f"📌 المرجع: {ref}")
        print(f"📜 النص: {text}...")

if __name__ == '__main__':
    run_test()
