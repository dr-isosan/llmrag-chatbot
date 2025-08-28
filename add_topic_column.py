#!/usr/bin/env python3
"""
Add topic column to questions database
"""

import sqlite3
from question_db import detect_topic

def add_topic_column():
    """Add topic column to questions table and populate it"""
    try:
        conn = sqlite3.connect('questions.db')
        c = conn.cursor()
        
        # Check if topic column exists
        c.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'topic' not in columns:
            print("Adding topic column...")
            c.execute('ALTER TABLE questions ADD COLUMN topic TEXT DEFAULT "genel"')
            print("✅ Topic column added successfully")
        else:
            print("✅ Topic column already exists")
        
        # Update existing questions with topics
        print("Updating existing questions with topics...")
        c.execute('SELECT id, question FROM questions WHERE topic IS NULL OR topic = "" OR topic = "genel"')
        rows = c.fetchall()
        
        print(f"Found {len(rows)} questions to update")
        
        for row_id, question in rows:
            if question:
                topic = detect_topic(question)
                c.execute('UPDATE questions SET topic = ? WHERE id = ?', (topic, row_id))
                print(f"Question {row_id}: '{question[:50]}...' -> {topic}")
        
        conn.commit()
        conn.close()
        print("✅ Database update completed successfully!")
        
        # Test the function
        print("\nTesting get_top_questions_with_topics...")
        from question_db import get_top_questions_with_topics
        result = get_top_questions_with_topics(3)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_topic_column()
