import sqlite3
from export_all import export_all
import sys

conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
c = conn.cursor()

# Check what we have for Nasai and Ibn Majah
c.execute("SELECT id, source_code, title_ar, status FROM sources WHERE title_ar LIKE '%نسائي%' OR title_ar LIKE '%ماجه%'")
rows = c.fetchall()
print("Found in sources:")
for r in rows:
    print(r)

# If they exist but have a different status, set it to ACTIVE
c.execute("UPDATE sources SET status = 'ACTIVE' WHERE title_ar LIKE '%نسائي%' OR title_ar LIKE '%ماجه%'")
conn.commit()

# Ensure that the chunks actually got inserted correctly and have the correct source_id
for r in rows:
    c.execute(f"SELECT count(*) FROM source_chunks WHERE source_id = '{r[0]}'")
    print(f"Chunks for {r[2]} ({r[0]}):", c.fetchone()[0])

print("Re-exporting...")
export_all()
