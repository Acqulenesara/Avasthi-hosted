import sys, traceback, os

# Run from C:\Users\acqul\PycharmProjects\flow
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'recom'))

print("=== Step 1: Load embeddings ===")
try:
    from recom.backend.dcl.utils import load_activity_embeddings, EMBED_PATH, TITLES_PATH
    print("EMBED_PATH:", EMBED_PATH, "| exists:", EMBED_PATH.exists())
    print("TITLES_PATH:", TITLES_PATH, "| exists:", TITLES_PATH.exists())
    emb = load_activity_embeddings()
    print("Embeddings loaded:", len(emb), "| dim:", next(iter(emb.values())).shape)
except Exception as e:
    traceback.print_exc()

print("\n=== Step 2: Load activities ===")
try:
    from recom.backend.recommendations.recommender import load_activities
    acts, amap = load_activities()
    print("Activities loaded:", len(acts))
    print("Sample:", list(amap.keys())[:3])
except Exception as e:
    traceback.print_exc()

print("\n=== Step 3: Load KG ===")
try:
    from recom.backend.recommendations.kg import load_kg_edges
    kg = load_kg_edges()
    print("KG loaded:", len(kg), "nodes")
except Exception as e:
    traceback.print_exc()

print("\n=== Step 4: Full recommend_activities with empty user data (new user) ===")
try:
    import numpy as np
    from recom.backend.recommendations.recommender import (
        recommend_activities, create_feedback_vector,
        create_short_term_intention_vector, W_LONG_TERM, W_SHORT_TERM, W_FEEDBACK,
    )
    from recom.backend.dcl.utils import load_activity_embeddings
    from recom.backend.recommendations.recommender import load_activities
    from recom.backend.recommendations.kg import load_kg_edges

    title_to_emb = load_activity_embeddings()
    acts, amap = load_activities()
    kg = load_kg_edges()
    embed_dim = next(iter(title_to_emb.values())).shape[0]

    # Check title overlap
    emb_titles = set(title_to_emb.keys())
    act_titles = set(amap.keys())
    overlap = emb_titles & act_titles
    print(f"Title overlap: {len(overlap)} / embeddings={len(emb_titles)} / activities={len(act_titles)}")
    missing_from_map = emb_titles - act_titles
    if missing_from_map:
        print("  Titles in embeddings but NOT in activity_map:", missing_from_map)

    # Simulate new user: no prefs, no msgs, no feedback
    feedback_vec = create_feedback_vector({}, title_to_emb, embed_dim)
    short_term_vec = create_short_term_intention_vector([])

    liked_vec = np.mean(list(title_to_emb.values()), axis=0)

    def safe_norm(v):
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    long_term_vec = safe_norm(liked_vec)
    w_lt, w_st, w_fb = W_LONG_TERM, W_SHORT_TERM, W_FEEDBACK

    if short_term_vec is None:
        w_lt += w_st
        w_st = 0.0
        short_term_vec = np.zeros(embed_dim)

    fused_vector = w_fb * feedback_vec + w_lt * long_term_vec + w_st * short_term_vec
    fused_vector = safe_norm(fused_vector)

    results = []
    for title, embedding in title_to_emb.items():
        if title not in amap:
            continue
        sim = float(np.dot(fused_vector, safe_norm(embedding)))
        results.append({"title": title, "score": round(sim, 4)})

    results.sort(key=lambda x: x["score"], reverse=True)
    print("Results count:", len(results))
    print("Top 5:", results[:5])
except Exception as e:
    traceback.print_exc()

print("\n=== Step 5: Test DB connection (Neon) ===")
try:
    from recom.backend.database import engine
    with engine.connect() as conn:
        from sqlalchemy import text
        row = conn.execute(text("SELECT 1")).fetchone()
        print("DB connected OK:", row)
except Exception as e:
    traceback.print_exc()

print("\n=== Step 6: Check tables & row counts ===")
try:
    from recom.backend.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        for table in ["users", "interactions", "user_preferences", "feedback"]:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table}: {count} rows")
            except Exception as te:
                print(f"  {table}: ERROR - {te}")
except Exception as e:
    traceback.print_exc()

print("\n=== Step 7: Full recommend via mock DB ===")
try:
    from unittest.mock import MagicMock
    mock_db = MagicMock()
    # Simulate UserPreference query
    mock_db.query.return_value.filter.return_value.all.return_value = []
    # Simulate ChatInteraction query (order_by + limit)
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    # Simulate Feedback query
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = recommend_activities(mock_db, "testuser", 8)
    print("Result count:", len(result) if result is not None else "None!")
    if result:
        print("Top rec:", result[0])
    else:
        print("EMPTY RESULT - recommend_activities returned [] or None")
except Exception as e:
    traceback.print_exc()

print("\n=== Step 8: Check POSTGRES_URL env var ===")
from dotenv import load_dotenv
load_dotenv('backend/.env')
load_dotenv('backend/recom/.env')
pg = os.environ.get('POSTGRES_URL', 'NOT SET')
print("POSTGRES_URL:", pg[:40] + "..." if len(pg) > 40 else pg)

print("\n=== Step 9: Test JWT decode with recom auth ===")
try:
    # Simulate what main.py does when creating a token
    import jwt as pyjwt
    from dotenv import load_dotenv
    load_dotenv('backend/recom/.env', override=False)
    SECRET = os.environ.get('SECRET_KEY', '')
    print(f"SECRET_KEY from env: '{SECRET}'")

    # Create a token the same way main.py does
    from datetime import datetime, timedelta
    token = pyjwt.encode({"sub": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET, algorithm="HS256")
    print(f"Token created: {token[:40]}...")

    # Now decode using the recom auth module
    from recom.backend.auth import extract_username_from_token
    username = extract_username_from_token(token)
    print(f"✅ Decoded username: {username}")
except Exception as e:
    traceback.print_exc()

print("\n=== Step 10: Full recommend with real DB for a real user ===")
try:
    from recom.backend.database import SessionLocal
    from recom.backend.recommendations.recommender import recommend_activities
    db = SessionLocal()
    # Use a real username from the DB
    from sqlalchemy import text
    with db.bind.connect() as conn:
        row = conn.execute(text("SELECT username FROM users LIMIT 1")).fetchone()
        real_user = row[0] if row else "testuser"
    print(f"Testing with real user: {real_user}")
    recs = recommend_activities(db, real_user, 8)
    print(f"✅ Got {len(recs)} recommendations")
    if recs:
        print(f"Top rec: {recs[0]['title']} (score: {recs[0]['score']})")
    db.close()
except Exception as e:
    traceback.print_exc()
