import sqlite3
import json
import os

def export_all():
    db_path = 'E:/basira/musnad-ai/apps/api/musnad_ai.db'
    out_path = 'E:/basira/musnad-ai/apps/api/app/data/all_sources.json'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = """
    SELECT 
        c.id as chunk_id,
        c.source_id,
        s.source_code,
        s.title as source_title,
        s.title_ar as source_title_ar,
        s.source_type,
        s.author,
        s.author_ar,
        s.edition,
        c.text,
        c.text_normalized,
        c.page,
        c.chapter,
        c.section,
        c.hadith_number,
        c.surah_number,
        c.verse_number,
        c.reference,
        c.grading,
        c.grading_authority
    FROM source_chunks c
    JOIN sources s ON c.source_id = s.id
    WHERE s.status IN ('ACTIVE', 'active')
    """
    
    c.execute(query)
    rows = c.fetchall()
    
    data = [dict(row) for row in rows]
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Exported {len(data)} chunks to {out_path}")

if __name__ == '__main__':
    export_all()
