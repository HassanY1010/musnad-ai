import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
c = conn.cursor()
c.execute("SELECT id, source_code, title_ar FROM sources")
print('In sources table:', c.fetchall())

c.execute("SELECT source_id, count(id) FROM source_chunks GROUP BY source_id")
for row in c.fetchall():
    print('Chunk counts:', row)
