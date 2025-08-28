from question_db import init_db
import sqlite3

DB_PATH = 'questions.db'

def show_all_questions():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, question, answer, created_at FROM questions ORDER BY id DESC")
    rows = c.fetchall()
    print(f"Toplam {len(rows)} soru bulundu:\n")
    for row in rows:
        qid, question, answer, created_at = row
        print(f"[{qid}] {created_at}\nSoru: {question}\nCevap: {answer[:120]}{'...' if len(answer)>120 else ''}\n{'-'*60}")
    conn.close()

if __name__ == "__main__":
    show_all_questions()
