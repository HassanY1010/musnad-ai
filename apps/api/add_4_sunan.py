import sqlite3
import json
import urllib.request
import uuid
import sys
import os

sys.path.append('E:/basira/musnad-ai/apps/api')
from app.services.text_utils import normalize_arabic
from export_all import export_all

def fetch_json(url):
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def ensure_source_exists(c, source_id, code, title, title_ar):
    c.execute("SELECT id FROM sources WHERE source_code = ?", (code,))
    row = c.fetchone()
    if row:
        return row[0]
        
    print(f"Adding source {title_ar}...")
    c.execute("""
        INSERT INTO sources 
        (id, source_code, title, title_ar, source_type, status, language, kb_version, created_at, updated_at) 
        VALUES (?, ?, ?, ?, 'HADITH', 'ACTIVE', 'ar', 'KB-002', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (source_id, code, title, title_ar))
    return source_id

def add_hadiths(c, source_id, url, prefix, book_name):
    print(f"Processing {book_name}...")
    try:
        data = fetch_json(url)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return
        
    c.execute(f"SELECT hadith_number FROM source_chunks WHERE source_id = '{source_id}'")
    existing_numbers = set([str(row[0]) for row in c.fetchall() if row[0] is not None])
    
    print(f"Found {len(existing_numbers)} existing hadiths for {book_name}.")
    
    inserts = []
    
    for h in data['hadiths']:
        h_num = str(h['hadithnumber'])
        if h_num in existing_numbers:
            continue
            
        text = h['text']
        if not text.strip():
            continue
            
        norm_text = normalize_arabic(text)
        chunk_id = f"hadith_{prefix}_{h_num}"
        ref = f"{book_name} - حديث رقم {h_num}"
        book = str(h['reference']['book'])
        
        inserts.append((
            chunk_id,
            'import', # document_id
            source_id,
            text,
            norm_text,
            book, # chapter
            h_num, # hadith_number
            ref
        ))
        
    print(f"Inserting {len(inserts)} new hadiths for {book_name}...")
    
    c.executemany("""
        INSERT INTO source_chunks 
        (id, document_id, source_id, text, text_normalized, chapter, hadith_number, reference, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, inserts)
    print(f"Finished {book_name}.")

def main():
    conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
    c = conn.cursor()

    sources_to_add = [
        ('c0eb64e5-0ebf-4905-9313-740284d64466', 'SRC-004', 'Sunan Abi Dawud', 'سنن أبي داود', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-abudawud.json', 'abudawud'),
        ('43ae143a-c75f-4afd-9e7c-e07699dcba69', 'SRC-005', 'Jami at-Tirmidhi', 'جامع الترمذي', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-tirmidhi.json', 'tirmidhi'),
        (str(uuid.uuid4()), 'SRC-006', 'Sunan al-Nasai', 'سنن النسائي', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nasai.json', 'nasai'),
        (str(uuid.uuid4()), 'SRC-007', 'Sunan Ibn Majah', 'سنن ابن ماجه', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-ibnmajah.json', 'ibnmajah')
    ]
    
    # Wait, uuid will change on re-run. Let's fix UUIDs for Nasai and Ibn Majah
    nasai_id = 'e5f5f5f5-f5f5-f5f5-f5f5-f5f5f5f5f5f5'
    ibnmajah_id = 'e6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6'
    
    sources_to_add[2] = (nasai_id, 'SRC-006', 'Sunan al-Nasai', 'سنن النسائي', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nasai.json', 'nasai')
    sources_to_add[3] = (ibnmajah_id, 'SRC-007', 'Sunan Ibn Majah', 'سنن ابن ماجه', 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-ibnmajah.json', 'ibnmajah')
    
    for s_id, s_code, s_title, s_title_ar, s_url, s_prefix in sources_to_add:
        real_id = ensure_source_exists(c, s_id, s_code, s_title, s_title_ar)
        add_hadiths(c, real_id, s_url, s_prefix, s_title_ar)
        conn.commit()
        
    conn.close()
    
    print("Exporting to JSON...")
    export_all()
    print("Done!")

if __name__ == '__main__':
    main()
