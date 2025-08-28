import sqlite3
from tabulate import tabulate

conn = sqlite3.connect('questions.db')
c = conn.cursor()

print('--- questions tablosu (son 5) ---')
c.execute('SELECT id, question, answer, answer_hash, keywords, created_at FROM questions ORDER BY id DESC LIMIT 5')
rows = c.fetchall()
print(tabulate(rows, headers=['id','question','answer','answer_hash','keywords','created_at']))

print('\n--- question_sources tablosu (son 5) ---')
c.execute('SELECT id, question_id, source_file FROM question_sources ORDER BY id DESC LIMIT 5')
rows = c.fetchall()
print(tabulate(rows, headers=['id','question_id','source_file']))

print('\n--- source_usage tablosu (tümü) ---')
c.execute('SELECT source_file, usage_count FROM source_usage ORDER BY usage_count DESC')
rows = c.fetchall()
print(tabulate(rows, headers=['source_file','usage_count']))

conn.close()
