import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
c = conn.cursor()
c.execute("SELECT id, source_code, title, title_ar FROM sources WHERE source_type = 'HADITH'")
print("Existing Hadith Sources:")
for row in c.fetchall():
    print(row)
