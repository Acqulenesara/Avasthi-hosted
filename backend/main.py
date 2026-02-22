from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import nltk
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, date
from sqlalchemy import MetaData, text, Column, Integer, String, Float, create_engine, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from databases import Database
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import psycopg2

# ── Load env FIRST so all os.getenv() calls work ─────────────────
load_dotenv(override=False)  # never overwrite env vars already set by Render

# ── Validate required env vars immediately ────────────────────────
DATABASE_URL = os.getenv("POSTGRES_URL") or ""
if not DATABASE_URL:
    raise RuntimeError("POSTGRES_URL environment variable is not set")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
ALGORITHM = "HS256"

# ── SQLAlchemy sync engine ────────────────────────────────────────
_sync_url = (DATABASE_URL
             .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
             .replace("postgresql://", "postgresql+psycopg2://")
             .split("?")[0])
_ssl_args = {"sslmode": "require"} if ("neon.tech" in DATABASE_URL or "sslmode=require" in DATABASE_URL) else {}

Base = declarative_base()
metadata = MetaData()
engine = create_engine(_sync_url, connect_args=_ssl_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Async DB (databases library) ─────────────────────────────────
database = Database(DATABASE_URL)

# ── HuggingFace LLM client ────────────────────────────────────────
from huggingface_hub import InferenceClient

hf_client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=os.getenv("HF_API_KEY"),
    timeout=45,
)

def llama_chat(messages, temperature=0.4):
    try:
        result = hf_client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=messages,
            max_tokens=300,
            temperature=temperature
        )
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        raise

# ── ORM Models ────────────────────────────────────────────────────

class Professional(Base):
    __tablename__ = "professionals"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    specialty = Column(String, index=True)
    bio = Column(String)
    availability_slots = relationship("AvailabilitySlot", back_populates="professional")
    appointments = relationship("Appointment", back_populates="professional")

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)
    professional = relationship("Professional", back_populates="availability_slots")
    appointment = relationship("Appointment", back_populates="slot")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_username = Column(String, ForeignKey("users.username"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    slot_id = Column(Integer, ForeignKey("availability_slots.id"), unique=True)
    status = Column(String, default="booked")
    meeting_link = Column(String, nullable=True)
    user = relationship("User", back_populates="appointments")
    professional = relationship("Professional", back_populates="appointments")
    slot = relationship("AvailabilitySlot", back_populates="appointment")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    preferences_collected = Column(Integer, default=0)
    stress_level = Column(Integer, default=0)
    appointments = relationship("Appointment", back_populates="user")

class ChatInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    query = Column(String)
    response = Column(String)
    scenario = Column(String, nullable=True)
    timestamp = Column(String, default=datetime.utcnow().isoformat)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    preference_type = Column(String)
    content = Column(String)
    __table_args__ = (UniqueConstraint('username', 'preference_type', 'content', name='uix_user_pref'),)

class JournalEntry(Base):
    __tablename__ = "journal_entry"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    entry_text = Column(String)
    entry_date = Column(Date)
    mood = Column(String)
    sentiment = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine)

# ── Routers (imported AFTER Base/engine are ready) ────────────────
from consult import router as consult_router

try:
    from diet.routes import router as diet_router
    app_include_diet = True
except Exception as _ex:
    print(f"⚠️ Diet router not loaded: {_ex}")
    diet_router = None
    app_include_diet = False

# ── psycopg2 PG config (for raw queries) ─────────────────────────
PG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDB", "mental_health_bot"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "1234")
}

def pg_conn(pg_conf=None):
    return psycopg2.connect(**(pg_conf or PG))

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pinecone ─────────────────────────────────────────────────────
pinecone_api_key = os.getenv("PINECONE_API_KEY")
cloud_region = "us-east-1"
embedding_dimension = 384
index_name = "flow-384"

pc = Pinecone(api_key=pinecone_api_key)
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="gcp", region=cloud_region.split("-")[1]),
    )
index = pc.Index(index_name)

# ── Auth helpers ──────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: timedelta = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=12))
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def extract_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── DB session dependency ─────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Lazy embedding model ──────────────────────────────────────────
_embedding_model = None

def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model

def get_embedding(text: str):
    try:
        return _get_embedding_model().encode(text).tolist()
    except Exception as e:
        print("❌ Failed to generate embedding:", e)
        return []

# ── Sentiment ─────────────────────────────────────────────────────
def analyze_sentiment_transformers(text):
    from textblob import TextBlob
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    return "neutral"

# ── Pinecone search ───────────────────────────────────────────────
def search_similar_text(query_text, top_k=5, score_threshold=0.3):
    query_vector = get_embedding(query_text)
    if not query_vector:
        return "No similar documents found."
    try:
        results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        contexts = [m.metadata["text"] for m in results.matches
                    if m.score >= score_threshold and "text" in m.metadata]
        return "\n".join(contexts) if contexts else "No similar documents found."
    except Exception as e:
        print("❌ Pinecone query failed:", e)
        return "No similar documents found."

# ── Pydantic models ───────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    password: str

class QueryPayload(BaseModel):
    query: str
    language: str = "en-US"

class JournalEntryRequest(BaseModel):
    entry: str

class JournalEntryResponse(BaseModel):
    entry_text: str
    entry_date: str
    mood: str
    sentiment: float

# ── Startup / Shutdown ────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await database.connect()
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    # ── Migrate journal_entry.sentiment from VARCHAR → DOUBLE PRECISION ──
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE journal_entry
                ALTER COLUMN sentiment TYPE DOUBLE PRECISION
                USING sentiment::DOUBLE PRECISION
            """))
            conn.commit()
            print("✅ journal_entry.sentiment migrated to DOUBLE PRECISION")
    except Exception:
        pass  # already numeric, or table doesn't exist yet

    try:
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE feedback
                ADD CONSTRAINT uix_feedback_user_activity
                UNIQUE (username, activity_title)
            """))
            conn.commit()
    except Exception:
        pass  # constraint already exists

    import asyncio
    async def _warm_up():
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, _get_embedding_model)
            print("✅ Embedding model warmed up")
        except Exception as e:
            print(f"⚠️ Embedding model warm-up failed: {e}")
    asyncio.create_task(_warm_up())
    print("🚀 Server ready — embedding model loading in background")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ── Health check ──────────────────────────────────────────────────
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Avasthi backend is running"}

# ── Auth endpoints ────────────────────────────────────────────────
@app.post("/register")
async def register_user(user: UserRegister):
    existing = await database.fetch_one("SELECT 1 FROM users WHERE username = :u", values={"u": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    await database.execute(
        "INSERT INTO users (username, password) VALUES (:username, :password)",
        values={"username": user.username, "password": get_password_hash(user.password)}
    )
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.fetch_one(
        "SELECT * FROM users WHERE username = :username",
        values={"username": form_data.username}
    )
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": create_access_token({"sub": user["username"]}), "token_type": "bearer"}

@app.get("/verify-token")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        from jose import jwt as jose_jwt, JWTError
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return {"valid": False}
        return {"valid": True, "username": username}
    except Exception:
        return {"valid": False}

# ── Chatbot endpoint ──────────────────────────────────────────────
async def get_conversation_history(username: str, limit: int = 10):
    try:
        rows = await database.fetch_all(
            "SELECT query, response FROM interactions WHERE username = :u ORDER BY timestamp DESC LIMIT :l",
            values={"u": username, "l": limit}
        )
        conversation = []
        for row in reversed(rows):
            conversation.append({"role": "user", "content": row["query"]})
            conversation.append({"role": "assistant", "content": row["response"]})
        return conversation
    except Exception as e:
        print("❌ Failed to fetch conversation history:", e)
        return []

def extract_context_from_text(text: str) -> dict:
    prompt = f"""Extract from this text a JSON with "scenario" (one of: family_conflict, academic_stress, work_pressure, relationship_issue, financial_stress, health_anxiety, social_anxiety, existential_crisis, grief_or_loss, self_doubt) and "role". Return ONLY the JSON.
Text: "{text}"
"""
    try:
        import json
        raw = llama_chat([{"role": "user", "content": prompt}], temperature=0.2)
        return json.loads(raw)
    except:
        return {"scenario": "unknown", "role": "user"}

def extract_preferences_from_chat(conversation: list) -> tuple:
    user_text = "\n".join([m["content"] for m in conversation if m["role"] == "user"])
    prompt = f"""From these messages extract preferences as JSON:
{{"preferences": [{{"type": "like"/"dislike", "content": "..."}}], "scenario": "..."}}
Messages: {user_text}"""
    try:
        import json
        raw = llama_chat([{"role": "user", "content": prompt}], temperature=0.2)
        result = json.loads(raw)
        return result.get("preferences", []), result.get("scenario", "unknown")
    except:
        return [], "unknown"

@app.post("/query")
async def handle_query(payload: QueryPayload, background_tasks: BackgroundTasks, token: str = Depends(oauth2_scheme)):
    try:
        import asyncio
        username = extract_username_from_token(token)
        query = payload.query
        loop = asyncio.get_event_loop()

        sentiment = analyze_sentiment_transformers(query)
        sentiment_instruction = {
            "positive": "Maintain an engaging and encouraging tone.",
            "neutral": "Respond normally with helpful advice.",
            "negative": "Keep it under 7 sentences. Use a compassionate tone. End with a short coping tip."
        }.get(sentiment, "Respond normally.")

        count = await database.fetch_val(
            "SELECT COUNT(*) FROM interactions WHERE username = :u", values={"u": username}
        )
        if (count or 0) <= 10:
            sentiment_instruction += " Ask one gentle question about their lifestyle or stress relief habits."

        instructions = f"You are Aarohi, a compassionate mental health assistant. Tone: {sentiment}.\n{sentiment_instruction}"

        conversation_history, retrieved_context = await asyncio.gather(
            get_conversation_history(username, limit=6),
            loop.run_in_executor(None, search_similar_text, query),
        )

        messages = [{"role": "system", "content": instructions}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": f"Context:\n{retrieved_context}\n\nUser: {query}"})

        response_text = await loop.run_in_executor(None, lambda: llama_chat(messages))

        background_tasks.add_task(_save_interaction_background, username, query, response_text, conversation_history)
        return {"thread_id": "llama", "response": response_text}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

async def _save_interaction_background(username, query, response_text, conversation_history):
    import asyncio
    loop = asyncio.get_running_loop()
    try:
        ctx = await loop.run_in_executor(None, lambda: extract_context_from_text(query))
        scenario = ctx.get("scenario", "unknown")
    except:
        scenario = "unknown"
    try:
        await database.execute(
            "INSERT INTO interactions (username, query, response, scenario, timestamp) VALUES (:username, :query, :response, :scenario, :timestamp)",
            values={"username": username, "query": query, "response": response_text, "scenario": scenario, "timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        print(f"❌ Failed to save interaction: {e}")
    try:
        full_conv = conversation_history + [{"role": "user", "content": query}, {"role": "assistant", "content": response_text}]
        prefs, _ = await loop.run_in_executor(None, lambda: extract_preferences_from_chat(full_conv))
        for pref in prefs:
            try:
                await database.execute(
                    "INSERT INTO user_preferences (username, preference_type, content) VALUES (:username, :preference_type, :content) ON CONFLICT DO NOTHING",
                    values={"username": username, "preference_type": pref.get("type", "like"), "content": pref.get("content", "")}
                )
            except:
                pass
    except Exception as e:
        print(f"❌ Failed to save preferences: {e}")

@app.get("/chat-history")
async def get_chat_history(token: str = Depends(oauth2_scheme)):
    username = extract_username_from_token(token)
    chats = await database.fetch_all(
        "SELECT * FROM interactions WHERE username = :u ORDER BY timestamp DESC LIMIT 100",
        values={"u": username}
    )
    return {"history": [dict(c) for c in chats]}

# ── Feedback endpoint ─────────────────────────────────────────────
from recom.backend.database import get_db as recom_get_db
from recom.backend.models import FeedbackRequest
from recom.backend.auth import extract_username_from_token as recom_extract_username, oauth2_scheme as recom_oauth2_scheme

@app.post("/feedback")
async def save_feedback(feedback: FeedbackRequest, db: Session = Depends(recom_get_db), token: str = Depends(oauth2_scheme)):
    username = extract_username_from_token(token)
    db.execute(text("""
        INSERT INTO feedback (username, activity_title, liked, timestamp)
        VALUES (:username, :activity_title, :liked, :timestamp)
        ON CONFLICT ON CONSTRAINT uix_feedback_user_activity
        DO UPDATE SET liked = EXCLUDED.liked, timestamp = EXCLUDED.timestamp
    """), {"username": username, "activity_title": feedback.activity_title, "liked": feedback.liked, "timestamp": datetime.utcnow()})
    db.commit()
    return {"message": "Feedback saved", "username": username, "activity": feedback.activity_title, "liked": feedback.liked}

# ── Journal endpoints ─────────────────────────────────────────────
from journal.sentiment import analyze_emotion

@app.post("/journal/submit", response_model=JournalEntryResponse)
async def submit_journal(entry_req: JournalEntryRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = extract_username_from_token(token)
    mood, scores = analyze_emotion(entry_req.entry)
    sentiment_score = float(scores[0]["score"])
    journal_entry = JournalEntry(
        username=username, entry_text=entry_req.entry,
        entry_date=date.today(), mood=mood, sentiment=sentiment_score
    )
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    return {"entry_text": journal_entry.entry_text, "entry_date": str(journal_entry.entry_date), "mood": journal_entry.mood, "sentiment": sentiment_score}

@app.get("/journal/entries", response_model=list[JournalEntryResponse])
async def get_journal_entries(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = extract_username_from_token(token)
    entries = db.query(JournalEntry).filter(JournalEntry.username == username).order_by(JournalEntry.entry_date.desc()).limit(5).all()
    return [{"entry_text": e.entry_text, "entry_date": str(e.entry_date), "mood": e.mood, "sentiment": float(e.sentiment) if e.sentiment is not None else 0.0} for e in entries]

# ── Include routers ───────────────────────────────────────────────
from recom.backend.routes.recommendations import router as rec_router
from excoach.routes import router as exercise_router

app.include_router(rec_router)
app.include_router(consult_router)
app.include_router(exercise_router)

if app_include_diet and diet_router is not None:
    try:
        app.include_router(diet_router)
    except Exception as ex:
        print("⚠️ Failed to include diet router:", ex)
