import sqlite3

conn = sqlite3.connect('E:/basira/musnad-ai/apps/api/musnad_ai.db')
c = conn.cursor()
c.execute("SELECT id, title_ar, status FROM sources")
for row in c.fetchall():
    print(row)
    
c.execute("UPDATE sources SET status = 'ACTIVE' WHERE title_ar LIKE '%نسائي%' OR title_ar LIKE '%ماجه%'")
conn.commit()
print("Updated statuses to ACTIVE")

from export_all import export_all
export_all()
