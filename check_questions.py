import sqlite3

DB_PATH = "questions.db"

def print_last_questions(n=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print(f"Son {n} soru ve cevaplar:")
    for row in c.execute("SELECT id, question, answer, created_at FROM questions ORDER BY id DESC LIMIT ?", (n,)):
        print(f"ID: {row[0]} | Soru: {row[1]}\nCevap: {row[2]}\nTarih: {row[3]}\n---")
    conn.close()

if __name__ == "__main__":
    print_last_questions(5)
