from textblob import TextBlob
import datetime
from enhanced_db import insert_entry

def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def submit_entry(conn, user_id, mood, entry_text, sentiment_score):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (user_id, entry_date, mood, entry, sentiment_score)
        VALUES (%s, CURRENT_DATE, %s, %s, %s)
    """, (user_id, mood, entry_text, sentiment_score))
    conn.commit()
    cursor.close()