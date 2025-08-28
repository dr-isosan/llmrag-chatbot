from question_db import get_total_questions, get_total_unique_questions, get_top_sources, get_top_questions_by_similarity, init_db

if __name__ == "__main__":
    try:
        init_db()  # Veritabanı ve tabloları oluştur
        print("Toplam Soru Sayısı:", get_total_questions())
        print("Benzersiz Soru Sayısı:", get_total_unique_questions())
        print("\nEn Fazla Kullanılan 5 Kaynak:")
        for idx, (source, count) in enumerate(get_top_sources(5), 1):
            print(f"{idx}. {source} ({count} kez)")
        print("\nEn Çok Sorulan 5 Soru (Benzerlik Analizine Göre):")
        for idx, (question, count) in enumerate(get_top_questions_by_similarity(5), 1):
            print(f"{idx}. {question} ({count} benzer)")
    except Exception as e:
        print("Hata oluştu:", e)