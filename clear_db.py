import sqlite3
import os

DB_PATH = "questions.db"

def clear_all_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM question_similarity")
    c.execute("DELETE FROM question_sources")
    c.execute("DELETE FROM questions")
    conn.commit()
    conn.close()
    print("Tüm veritabanı tabloları temizlendi.")

def clear_all_tables_and_stats():
    # Veritabanı tablolarını temizle
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM question_similarity")
    c.execute("DELETE FROM question_sources")
    c.execute("DELETE FROM questions")
    c.execute("DELETE FROM source_usage")
    conn.commit()
    conn.close()
    # İstatistik dosyasını sıfırla
    stats_path = "stats.json"
    if os.path.exists(stats_path):
        with open(stats_path, "w", encoding="utf-8") as f:
            f.write('{\n  "lastQA": [],\n  "topKeywords": [],\n  "topQuestions": [],\n  "topSources": [],\n  "totalQuestions": 0,\n  "uniqueQuestions": 0\n}\n')
        print("stats.json sıfırlandı.")
    print("Tüm veritabanı tabloları ve istatistikler temizlendi.")

if __name__ == "__main__":
    clear_all_tables_and_stats()
