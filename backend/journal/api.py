from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from enhanced_db import get_connection, insert_entry, fetch_entries_by_user, create_user, verify_user
from sentiment import analyze_emotion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EntryRequest(BaseModel):
    user_id: int
    entry: str

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(data: SignupRequest):
    conn = get_connection()
    try:
        create_user(conn, data.username, data.email, data.password)
        return {"message": "Signup successful"}
    except ValueError as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.post("/login")
def login(data: LoginRequest):
    conn = get_connection()
    user_id = verify_user(conn, data.username, data.password)
    conn.close()
    return {"user_id": user_id}

@app.post("/submit")
def submit_entry_api(data: EntryRequest):
    mood, scores = analyze_emotion(data.entry)
    conn = get_connection()
    insert_entry(conn, data.user_id, entry_date=date.today(), mood=mood, entry_text=data.entry, sentiment=scores[0]['score'])
    conn.close()
    return {"mood": mood, "sentiment": scores[0]['score'], "details": scores}

@app.get("/entries/{user_id}")
def get_entries(user_id: int):
    conn = get_connection()
    entries = fetch_entries_by_user(conn, user_id, limit=5)
    conn.close()
    return entries