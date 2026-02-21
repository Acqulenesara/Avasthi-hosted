import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="mental_health_bot",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

def create_user(conn, username, email, password):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("Username already exists")
    finally:
        cursor.close()

def verify_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT id, hashed_password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()

    if result and result[1] == password:
        return result[0]
    return None

def insert_entry(conn, user_id, entry_date, mood, entry_text, sentiment):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (user_id, entry_date, mood, entry, sentiment_score)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, entry_date, mood, entry_text, sentiment))
    conn.commit()
    cursor.close()

def fetch_entries_by_user(conn, user_id, limit=5):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entry_date, mood, sentiment_score, entry
        FROM journal_entries
        WHERE user_id = %s
        ORDER BY entry_date DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    return [
        {
            "entry_date": row[0],
            "mood": row[1],
            "sentiment_score": row[2],
            "entry": row[3]
        } for row in rows
    ]