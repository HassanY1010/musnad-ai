import sqlite3

def update_sources_metadata():
    db_paths = ['apps/api/musnad_ai.db', 'musnad_ai.db']
    
    updates = [
        ('SRC-007', 'التفسير الميسر', 'نخبة من أساتذة التفسير', 'مجمع الملك فهد لطباعة المصحف الشريف', 'طبعة مجمع الملك فهد', 'Public Domain', 'Verified Tafsir edition'),
        ('SRC-008', 'موسوعة الآثار وأقوال أئمة الإسلام المعتمدة', 'كبار الأئمة والفقهاء', 'دار المنهاج / مؤسسة الرسالة', 'طبعة محققة معتمدة', 'Public Domain', 'Classical Scholarly Compilations'),
        ('SRC-009', 'سجل المراجع والقرارات الفقهية والمجمعية المعتمدة', 'مجامع الفقه الإسلامي الدولي', 'مجمع الفقه الإسلامي الدولي', 'قرارات المجامع الفقهية المعتمدة', 'Institutional Resolutions', 'Verified Fiqh Academy Resolutions'),
        ('SRC-010', 'سنن النسائي', 'الإمام أحمد بن شعيب النسائي (ت 303 هـ)', 'دار التأصيل / مؤسسة الرسالة', 'السنن الصغرى (المجتبى)', 'Public Domain', 'Classical Sunan collection'),
        ('SRC-011', 'سنن ابن ماجه', 'الإمام محمد بن يزيد بن ماجه (ت 273 هـ)', 'دار إحياء الكتب العربية / الرسالة', 'طبعة محققة معتمدة', 'Public Domain', 'Classical Sunan collection'),
    ]
    
    for db_path in db_paths:
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            for code, title_ar, author_ar, publisher, edition, license_type, prov in updates:
                c.execute('''
                    UPDATE sources 
                    SET title_ar = COALESCE(title_ar, ?),
                        author_ar = COALESCE(author_ar, ?),
                        publisher = ?,
                        edition = COALESCE(edition, ?),
                        license = ?,
                        provenance = ?
                    WHERE source_code = ?
                ''', (title_ar, author_ar, publisher, edition, license_type, prov, code))
            conn.commit()
            print(f"Successfully updated metadata in {db_path}")
            
            c.execute("SELECT source_code, title_ar, publisher, license FROM sources")
            for r in c.fetchall():
                print(" ", r)
            conn.close()
        except Exception as e:
            print(f"Error updating {db_path}: {e}")

if __name__ == '__main__':
    update_sources_metadata()
