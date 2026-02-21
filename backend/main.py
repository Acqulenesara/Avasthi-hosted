from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import nltk
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
load_dotenv()

# from recommender.rec_inference import Recommender, PG
from huggingface_hub import InferenceClient
import os

hf_client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_API_KEY")
)

def llama_chat(messages, temperature=0.4):
    result = hf_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=messages,
        max_tokens=300,
        temperature=temperature
    )
    return result.choices[0].message.content


import os
DATABASE_URL = os.getenv("POSTGRES_URL")

# SQLAlchemy setup
Base = declarative_base()
metadata = MetaData()

# ... (near your other model imports)
from sqlalchemy import Column, Integer, String, create_engine, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


# --- Import the new router ---
from consult import router as consult_router

class Professional(Base):
    __tablename__ = "professionals"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    specialty = Column(String, index=True)  # e.g., "CBT", "Anxiety", "Grief Counseling"
    bio = Column(String)

    # Relationships
    availability_slots = relationship("AvailabilitySlot", back_populates="professional")
    appointments = relationship("Appointment", back_populates="professional")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)

    # Relationships
    professional = relationship("Professional", back_populates="availability_slots")
    appointment = relationship("Appointment", back_populates="slot")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_username = Column(String, ForeignKey("users.username"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    slot_id = Column(Integer, ForeignKey("availability_slots.id"), unique=True)
    status = Column(String, default="booked")  # e.g., "booked", "completed", "cancelled"
    meeting_link = Column(String, nullable=True)  # You could generate a Zoom/Meet link here

    # Relationships
    user = relationship("User", back_populates="appointments")
    professional = relationship("Professional", back_populates="appointments")
    slot = relationship("AvailabilitySlot", back_populates="appointment")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    preferences_collected = Column(Integer, default=0)  # 0 = no, 1 = yes

    stress_level = Column(Integer, default=0)  # 0 = low, 5 = high

    # --- ADD THIS RELATIONSHIP ---
    appointments = relationship("Appointment", back_populates="user")


class ChatInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    query = Column(String)
    response = Column(String)
    scenario = Column(String, nullable=True)
    timestamp = Column(String, default=datetime.utcnow().isoformat)

# Add to SQLAlchemy models
from sqlalchemy.schema import UniqueConstraint

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    preference_type = Column(String)
    content = Column(String)

    __table_args__ = (UniqueConstraint('username', 'preference_type', 'content', name='uix_user_pref'),)
       # e.g., yoga, music, solitude


# Use databases for async DB interaction
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL.replace("asyncpg", "psycopg2").split("?")[0])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (you can also run Alembic migrations)
Base.metadata.create_all(bind=engine)


# Download necessary NLTK data
nltk.download("punkt")

# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables

#openai.api_key = os.getenv("OPENAI_API_KEY")


PG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDB", "mental_health_bot"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "1234")
}

# ---------------------------
# DB utility
# ---------------------------
import psycopg2

def pg_conn(pg_conf=PG):
    return psycopg2.connect(**pg_conf)

# FastAPI App Initialization
app = FastAPI()

# Add CORS middleware
# Bearer token auth doesn't need credentials=True (that's for cookies).
# Using allow_origins=["*"] with allow_credentials=False is correct here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#recommender = Recommender(pg_conf=PG, embedding_dim=128, device="cpu")

# JWT Secret Key
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = datetime.utcnow() + timedelta(hours=12)

pinecone_api_key = "pcsk_5D1v7g_MTTv3ZifoaK9ffLM5kZMyuL3HN2Kjc6jWDjjt6jHdWFqftdFHdc2AyfHBqXTKqQ"
cloud_region = "us-east-1"
embedding_dimension = 384
index_name = "flow-384"

global query_history
query_history = ""

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="gcp", region=cloud_region.split("-")[1]),
    )
index = pc.Index(index_name)


# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")



# truncate to 72 bytes before hashing/verifying
def verify_password(plain_password, hashed_password):
    truncated_password = plain_password[:72]  # truncate to max 72 bytes
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password):
    truncated_password = password[:72]  # truncate to max 72 bytes
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_username(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# User Authentication
class UserRegister(BaseModel):
    username: str
    password: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/register")
async def register_user(user: UserRegister):
    query = "SELECT * FROM users WHERE username = :username"
    existing_user = await database.fetch_one(query=query, values={"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    insert_query = "INSERT INTO users (username, password) VALUES (:username, :password)"
    await database.execute(query=insert_query, values={"username": user.username, "password": hashed_password})
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = "SELECT * FROM users WHERE username = :username"
    user = await database.fetch_one(query=query, values={"username": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # ✅ Must use user["username"] dynamically
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# Pydantic model for request handling

class QueryPayload(BaseModel):
    query: str
    language: str = "en-US"  # optional, sent by frontend


# Load the sentiment analysis model from NLP Town
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    framework="pt"
)



# Function to analyze sentiment
def analyze_sentiment_transformers(text):
    result = sentiment_pipeline(text)[0]
    label = result['label']  # e.g., '4 stars'
    rating = int(label.split()[0])  # extract the number from 'X stars'

    # You can customize the label to your format (e.g., positive, neutral, negative)
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"

from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Replace get_embedding with OpenAI Embedding
def get_embedding(text: str) -> list[float]:
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        print("❌ Failed to generate embedding:", e)
        return []

# Function to retrieve similar documents from ChromaDB
def search_similar_text(query_text, top_k=5, score_threshold=0.3):
    query_vector = get_embedding(query_text)

    if not query_vector:
        return "No similar documents found."

    try:
        pinecone_results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        retrieved_contexts = []
        for match in pinecone_results.matches:
            if match.score >= score_threshold and "text" in match.metadata:
                retrieved_contexts.append(match.metadata["text"])

        return "\n".join(retrieved_contexts) if retrieved_contexts else "No similar documents found."

    except Exception as e:
        print("❌ Pinecone query failed:", e)
        return "No similar documents found."


def extract_context_from_text(text: str) -> dict:
    prompt = f"""
    You are an NLP assistant helping another assistant understand emotional context.

    Task: From the user's message, extract:
    - scenario: one of ["family_conflict", "academic_stress", "work_pressure", "relationship_issue", "financial_stress", "health_anxiety", "social_anxiety", "existential_crisis", "grief_or_loss", "self_doubt"]
    - role: their position in the situation (e.g., daughter, son, student, employee, partner, friend, patient)


    Return a JSON object only, like:
    {{ "scenario": "relationship_issue", "role": "partner" }}

    Example:
    Text: "I got into a fight with my dad. He doesn't understand me."
    -> {{ "scenario": "family_conflict", "role": "daughter" }}

    Text: "I failed two tests and I don't think I can pass this semester."
    -> {{ "scenario": "academic_stress", "role": "student" }}

    Now analyze this:
    Text: "{text}"
    """

    try:
        raw = llama_chat([{"role": "user", "content": prompt}], temperature=0.2)
        import json
        return json.loads(raw)
    except:
        return {"scenario": "unknown", "role": "user"}


def extract_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")  # "sub" usually stores the username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def extract_preferences_from_chat(conversation: list[dict]) -> tuple[list[dict], str]:
    """
    Extract preferences + scenario only from user messages in a chat history.
    """
    user_text = "\n".join([msg["content"] for msg in conversation if msg["role"] == "user"])

    prompt = f"""
    Analyze the following chat messages written by the user. 
    Extract two things:
    1. Preferences related to stress relief, lifestyle, hobbies, or dislikes as a list of JSON objects like:
    [{{"type": "like", "content": "meditation"}}, {{"type": "dislike", "content": "loud places"}}]

    2. Do **not** assume relationships or personal contexts unless the user clearly mentions them.
   If vague (e.g., just "I had a fight"), return a general label like "conflict" or leave the scenario as "".
    User Messages:
    {user_text}

    Return your response as:
    {{
        "preferences": [...],
        "scenario": "..."
    }}
    """

    try:
        raw = llama_chat([{"role": "user", "content": prompt}], temperature=0.2)
        import json
        result = json.loads(raw)
        return result.get("preferences", []), result.get("scenario", "unknown")
    except:
        return [], "unknown"


async def get_conversation_history(username: str, limit: int = 10) -> list[dict]:
    """
    Fetch the last N interactions for the user and return them as a conversation list.
    Format: [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]
    """
    try:
        query = """
            SELECT query, response FROM interactions
            WHERE username = :username
            ORDER BY timestamp DESC
            LIMIT :limit
        """
        rows = await database.fetch_all(query=query, values={"username": username, "limit": limit})

        # Reverse so it's in chronological order
        conversation = []
        for row in reversed(rows):
            conversation.append({"role": "user", "content": row["query"]})
            conversation.append({"role": "assistant", "content": row["response"]})

        return conversation

    except Exception as e:
        print("❌ Failed to fetch conversation history:", e)
        return []


@app.post("/query")
async def handle_query(payload: QueryPayload, background_tasks: BackgroundTasks, token: str = Depends(oauth2_scheme)):
    try:
        import asyncio
        username = extract_username_from_token(token)
        query = payload.query

        loop = asyncio.get_event_loop()

        # 1. Sentiment is fast (local model), run directly
        sentiment = analyze_sentiment_transformers(query)

        # 2. Build instructions
        sentiment_instruction = {
            "positive": "Maintain an engaging and encouraging tone.",
            "neutral": "Respond normally with helpful advice.",
            "negative": "Keep it under 7 sentences. Use a compassionate tone. End with a short coping tip. Keep it short."
        }.get(sentiment, "Respond normally. Be concise and to the point.")

        interaction_count_query = "SELECT COUNT(*) FROM interactions WHERE username = :username"
        interaction_count = await database.fetch_val(query=interaction_count_query, values={"username": username})

        if interaction_count <= 10:
            sentiment_instruction += (
                " Ask one gentle question about their lifestyle or stress relief habits."
            )

        instructions = (
            f"You are Aarohi, a compassionate mental health assistant. "
            f"Tone: {sentiment}.\n{sentiment_instruction}"
        )

        # 3. Fetch conversation history (fast DB call)
        conversation_history = await get_conversation_history(username, limit=6)

        # 4. Pinecone search in thread (sync call, don't block event loop)
        retrieved_context = await loop.run_in_executor(None, search_similar_text, query)

        # 5. Build messages and call LLM (single blocking call, run in thread)
        messages = [{"role": "system", "content": instructions}]
        messages.extend(conversation_history)
        messages.append({
            "role": "user",
            "content": f"Context:\n{retrieved_context}\n\nUser: {query}"
        })

        response_text = await loop.run_in_executor(None, lambda: llama_chat(messages))

        # 6. Save to DB and extract preferences IN THE BACKGROUND after responding
        background_tasks.add_task(
            _save_interaction_background,
            username, query, response_text, conversation_history
        )

        return {"thread_id": "llama", "response": response_text}

    except Exception as e:
        import traceback
        print("❌ Error in /query:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


async def _save_interaction_background(username: str, query: str, response_text: str, conversation_history: list):
    """Runs AFTER the response is already sent — saves interaction + preferences to DB."""
    import asyncio
    loop = asyncio.get_running_loop()

    # Determine scenario without blocking main request
    try:
        context = await loop.run_in_executor(None, lambda: extract_context_from_text(query))
        scenario = context.get("scenario", "unknown")
    except Exception:
        scenario = "unknown"

    # Save the interaction
    try:
        await database.execute(
            query="""
                INSERT INTO interactions (username, query, response, scenario, timestamp)
                VALUES (:username, :query, :response, :scenario, :timestamp)
            """,
            values={
                "username": username,
                "query": query,
                "response": response_text,
                "scenario": scenario,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        print(f"✅ Saved interaction for {username}")
    except Exception as db_err:
        print(f"❌ Failed to save interaction: {db_err}")

    # Extract and save preferences
    try:
        full_conversation = conversation_history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response_text}
        ]
        preferences, _ = await loop.run_in_executor(
            None, lambda: extract_preferences_from_chat(full_conversation)
        )
        for pref in preferences:
            try:
                await database.execute(
                    query="""
                        INSERT INTO user_preferences (username, preference_type, content)
                        VALUES (:username, :preference_type, :content)
                        ON CONFLICT DO NOTHING
                    """,
                    values={
                        "username": username,
                        "preference_type": pref.get("type", "like"),
                        "content": pref.get("content", "")
                    }
                )
            except Exception:
                pass
    except Exception as pref_err:
        print(f"❌ Failed to extract preferences: {pref_err}")


from jose import JWTError, jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@app.get("/verify-token")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return {"valid": False}
        return {"valid": True, "username": username}
    except JWTError:
        return {"valid": False}


@app.get("/chat-history")
async def get_chat_history(token: str = Depends(oauth2_scheme)):
    username = extract_username_from_token(token)
    query = "SELECT * FROM interactions WHERE username = :username ORDER BY timestamp DESC LIMIT 100"
    chats = await database.fetch_all(query=query, values={"username": username})
    return {"history": [dict(chat) for chat in chats]}

# from recom.backend.recommendations.recommender import recommend_activities
#
# @app.get("/recommendations")
# async def get_recommendations(
#     token: str = Depends(oauth2_scheme),
#     top_k: int = 10
# ):
#     username = extract_username_from_token(token)
#     recs = recommend_activities(username, top_k=top_k)
#     return {"username": username, "recommendations": recs}

from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime
from recom.backend.database import get_db
from recom.backend.models import FeedbackRequest
from recom.backend.auth import extract_username_from_token, oauth2_scheme



@app.post("/feedback")
async def save_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    username = extract_username_from_token(token)

    from sqlalchemy import text

    insert_stmt = text("""
    INSERT INTO feedback (username, activity_title, liked, timestamp)
    VALUES (:username, :activity_title, :liked, :timestamp)
    ON CONFLICT (username, activity_title)
    DO UPDATE SET liked = EXCLUDED.liked, timestamp = EXCLUDED.timestamp
    """)


    params = {
        "username": username,
        "activity_title": feedback.activity_title,
        "liked": feedback.liked,
        "timestamp": datetime.utcnow()
    }

    db.execute(insert_stmt, params)
    db.commit()

    return {
        "message": "Feedback saved via raw SQL",
        "username": username,
        "activity": feedback.activity_title,
        "liked": feedback.liked
    }

@app.get("/recommendation-history")
async def get_user_history(token: str = Depends(oauth2_scheme)):
    username = extract_username_from_token(token)

    import psycopg2
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    cur.execute("""
        SELECT query, timestamp
        FROM interactions
        WHERE username = %s
        ORDER BY timestamp DESC
        LIMIT 10
    """, (username,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {"username": username, "history": [{"query": q, "timestamp": str(ts)} for q, ts in rows]}

from sqlalchemy import Date

class JournalEntry(Base):
    __tablename__ = "journal_entry"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    entry_text = Column(String)
    entry_date = Column(Date)
    mood = Column(String)
    sentiment = Column(String)


from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import date
from journal.sentiment import analyze_emotion  # Import your sentiment.py function

# Pydantic schemas
class JournalEntryRequest(BaseModel):
    entry: str

class JournalEntryResponse(BaseModel):
    entry_text: str
    entry_date: str
    mood: str
    sentiment: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/journal/submit", response_model=JournalEntryResponse)
async def submit_journal(entry_req: JournalEntryRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = extract_username_from_token(token)

    mood, scores = analyze_emotion(entry_req.entry)
    sentiment_score = scores[0]["score"]

    journal_entry = JournalEntry(
        username=username,
        entry_text=entry_req.entry,
        entry_date=date.today(),
        mood=mood,
        sentiment=str(sentiment_score)
    )

    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)

    return {
        "entry_text": journal_entry.entry_text,
        "entry_date": str(journal_entry.entry_date),
        "mood": journal_entry.mood,
        "sentiment": sentiment_score
    }


@app.get("/journal/entries", response_model=list[JournalEntryResponse])
async def get_journal_entries(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = extract_username_from_token(token)

    entries = db.query(JournalEntry).filter(JournalEntry.username == username).order_by(JournalEntry.entry_date.desc()).limit(5).all()

    return [
        {
            "entry_text": e.entry_text,
            "entry_date": str(e.entry_date),
            "mood": e.mood,
            "sentiment": float(e.sentiment)
        } for e in entries
    ]


from recom.backend.routes.recommendations import router as rec_router

app.include_router(rec_router)
app.include_router(consult_router)

from excoach.routes import router as exercise_router
app.include_router(exercise_router)

# Health check - keeps Render from sleeping & used as wake-up ping
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Avasthi backend is running"}
