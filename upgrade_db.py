#!/usr/bin/env python3
import sqlite3

def upgrade_database():
    print("🔄 Veritabanı güncelleniyor...")
    
    conn = sqlite3.connect("questions.db")
    c = conn.cursor()
    
    try:
        # Mevcut kolonları kontrol et
        c.execute("PRAGMA table_info(questions)")
        columns = c.fetchall()
        existing_columns = [col[1] for col in columns]
        print(f"📋 Mevcut kolonlar: {existing_columns}")
        
        # Yeni kolonları ekle
        if 'source_file' not in existing_columns:
            c.execute("ALTER TABLE questions ADD COLUMN source_file TEXT")
            print("✅ source_file kolonu eklendi")
        
        if 'source_keyword' not in existing_columns:
            c.execute("ALTER TABLE questions ADD COLUMN source_keyword TEXT")
            print("✅ source_keyword kolonu eklendi")
        
        conn.commit()
        
        # Güncellenmiş şemayı kontrol et
        c.execute("PRAGMA table_info(questions)")
        columns = c.fetchall()
        print("📋 Güncellenmiş tablo şeması:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("✅ Veritabanı başarıyla güncellendi!")
        
    except Exception as e:
        print(f"❌ Güncelleme hatası: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_database()
