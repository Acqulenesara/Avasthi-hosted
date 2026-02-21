
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import uvicorn

from recommender.rec_inference import Recommender, PG

# ---------------------------
# Initialize FastAPI
# ---------------------------
app = FastAPI(title="Mental Health Recommendation API")

# Allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # in production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load recommender once at startup
recommender = Recommender(pg_conf=PG, embedding_dim=128, device="cpu")

# ---------------------------
# Endpoints
# ---------------------------

@app.get("/")
def root():
    return {"message": "Welcome to the Mental Health Recommender API"}

@app.get("/recommendations")
def get_recommendations(username: str = Query(...), top_k: int = Query(5)):
    try:
        recs = recommender.recommend_for_username(username, top_k=top_k)
        #print("DEBUG Recommendations:", recs)  # 👈 add this
        return {"username": username, "recommendations": recs}
    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}




from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    username: str
    activity_title: str
    liked: bool


@app.post("/feedback")
def save_feedback(feedback: FeedbackRequest):
    import psycopg2
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()

    # look up entity_id from title
    cur.execute("SELECT id FROM activities WHERE title = %s", (feedback.activity_title,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": f"Activity '{feedback.activity_title}' not found"}
    print("Looking up:", feedback.activity_title, flush=True)

    entity_id = row[0]
    pref_type = "like" if feedback.liked else "dislike"

    cur.execute("""
        INSERT INTO user_preferences (username, entity_id, preference_type, source)
        VALUES (%s, %s, %s, 'button')
        ON CONFLICT (username, entity_id, source)
        DO UPDATE SET preference_type = EXCLUDED.preference_type;
    """, (feedback.username, entity_id, pref_type))

    conn.commit()
    cur.close()
    conn.close()
    return {
        "message": "Feedback saved",
        "username": feedback.username,
        "activity": feedback.activity_title,
        "liked": feedback.liked
    }


@app.get("/history")
def get_user_history(username: str):
    """
    Fetch past interactions for a user.
    """
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

# ---------------------------





# Run server
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)