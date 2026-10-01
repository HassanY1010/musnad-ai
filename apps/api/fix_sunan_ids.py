import sqlite3
import uuid
import sys
from export_all import export_all

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
c = conn.cursor()

# 1. Create Nasai source
nasai_id = str(uuid.uuid4())
c.execute("""
    INSERT INTO sources (id, source_code, title, title_ar, source_type, status, language, kb_version, created_at, updated_at) 
    VALUES (?, 'SRC-010', 'Sunan al-Nasai', 'سنن النسائي', 'HADITH', 'ACTIVE', 'ar', 'KB-002', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
""", (nasai_id,))

# 2. Create Ibn Majah source
ibnmajah_id = str(uuid.uuid4())
c.execute("""
    INSERT INTO sources (id, source_code, title, title_ar, source_type, status, language, kb_version, created_at, updated_at) 
    VALUES (?, 'SRC-011', 'Sunan Ibn Majah', 'سنن ابن ماجه', 'HADITH', 'ACTIVE', 'ar', 'KB-002', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
""", (ibnmajah_id,))

# 3. Update source_id for Nasai chunks
c.execute("UPDATE source_chunks SET source_id = ? WHERE id LIKE 'hadith_nasai_%'", (nasai_id,))

# 4. Update source_id for Ibn Majah chunks
c.execute("UPDATE source_chunks SET source_id = ? WHERE id LIKE 'hadith_ibnmajah_%'", (ibnmajah_id,))

conn.commit()

print("Fixed Nasai and Ibn Majah sources!")
export_all()
