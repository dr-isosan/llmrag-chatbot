#!/usr/bin/env python3
import sqlite3
import os

def recreate_database():
    print("🔄 Veritabanı yeniden oluşturuluyor...")
    
    # Eski veritabanını sil
    if os.path.exists("questions.db"):
        os.remove("questions.db")
        print("🗑️ Eski veritabanı silindi")
    
    # Yeni veritabanını oluştur
    from question_db import init_db
    init_db()
    print("✅ Yeni veritabanı oluşturuldu")
    
    # Veritabanı şemasını kontrol et
    conn = sqlite3.connect("questions.db")
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(questions)")
    columns = c.fetchall()
    print("📋 Questions tablosu kolonları:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("✅ Veritabanı başarıyla yeniden oluşturuldu!")

if __name__ == "__main__":
    recreate_database()
