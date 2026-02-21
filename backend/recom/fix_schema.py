from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT, likes TEXT DEFAULT '', dislikes TEXT DEFAULT '', preferences_collected BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW());"))
    conn.execute(text("CREATE TABLE IF NOT EXISTS feedback (id SERIAL PRIMARY KEY, username TEXT, activity_title TEXT, liked BOOLEAN, timestamp TIMESTAMP DEFAULT NOW());"))
    conn.commit()

print("✅ Tables created or updated")