#!/usr/bin/env python3
import sqlite3
from question_db import init_db, get_total_questions, get_top_sources, get_top_questions_by_similarity

# Test veritabanı fonksiyonları
def test_db_functions():
    print("🔄 Veritabanı test ediliyor...")
    
    try:
        # Veritabanını başlat
        init_db()
        print("✅ Veritabanı başlatıldı")
        
        # Toplam soru sayısı
        total = get_total_questions()
        print(f"📊 Toplam soru sayısı: {total}")
        
        # En çok kullanılan kaynaklar
        top_sources = get_top_sources(5)
        print(f"📂 En çok kullanılan kaynaklar: {top_sources}")
        
        # En çok sorulan sorular
        top_questions = get_top_questions_by_similarity(5)
        print(f"❓ En çok sorulan sorular: {top_questions}")
        
        print("✅ Tüm testler başarılı!")
        
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_functions()
