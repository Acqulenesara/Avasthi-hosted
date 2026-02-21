# in recommendations/recommender.py

import numpy as np
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import traceback
import csv
from pathlib import Path

from ..data_access import get_user_preferences, get_recent_interactions, get_user_feedback_from_db
from ..dcl.utils import load_activity_embeddings
from .kg import load_kg_edges

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_activities():
    """Loads activities and creates a quick title-to-activity lookup map."""
    try:
        with open(DATA_DIR / "activities.csv", newline='', encoding='utf-8') as f:
            activities = list(csv.DictReader(f))
            activity_map = {act['title']: act for act in activities}
            return activities, activity_map
    except FileNotFoundError:
        print("Warning: activities.csv not found. Returning empty list and map.")
        return [], {}


def format_rationale(raw_str: str) -> str:
    phrases = []
    for part in raw_str.split("; "):
        if "HAS_MODALITY" in part:
            modality = part.split("::")[-1]
            phrases.append(f"is {modality}")
        elif "HAS_DURATION" in part:
            duration = part.split("::")[-1]
            phrases.append(f"takes {duration}")
        elif "REQUIRES" in part:
            env = part.split("::")[-1]
            phrases.append(f"can be done in {env}")
        elif "CONTRAINDICATED_FOR" in part and "NaN" not in part:
            contraindication = part.split("::")[-1]
            phrases.append(f"not recommended for {contraindication}")
    return "This activity " + ", ".join(phrases) + "." if phrases else "No rationale available."


def build_rationale(title, kg):
    attrs = kg.get(title, {})
    rationale_parts = []
    for rel, targets in attrs.items():
        unique_targets = list(set(targets))
        for target in unique_targets:
            rationale_parts.append(f"{rel}={target}")
    return format_rationale("; ".join(rationale_parts))


CONTEXT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
# --- NEW, TUNED WEIGHTS ---
W_LONG_TERM = 0.15
W_SHORT_TERM = 0.55 # Reduced from 0.5
W_FEEDBACK = 0.3    # Increased from 0.3


def create_feedback_vector(feedback: dict, embeddings: dict, dim: int) -> np.ndarray:
    liked_vecs = [embeddings[title] for title, liked in feedback.items() if liked and title in embeddings]
    disliked_vecs = [embeddings[title] for title, liked in feedback.items() if not liked and title in embeddings]

    if not liked_vecs and not disliked_vecs:
        return np.zeros(dim)

    like_mean = np.mean(liked_vecs, axis=0) if liked_vecs else np.zeros(dim)
    dislike_mean = np.mean(disliked_vecs, axis=0) if disliked_vecs else np.zeros(dim)

    return like_mean - 0.5 * dislike_mean


def create_short_term_intention_vector(messages: list) -> np.ndarray:
    if not messages:
        return None
    full_context_text = ". ".join(messages)
    vec = CONTEXT_MODEL.encode(full_context_text)
    return vec




def recommend_activities(
        db: Session,
        username: str,
        top_k: int,
        use_short_term: bool = True,  # Flag for short-term context
        use_long_term: bool = True,  # Flag for long-term preferences
        use_feedback: bool = True  # Flag for explicit feedback
):
    """
    Recommends activities using a fused profile.
    Includes boolean flags to disable components for ablation studies.
    """
    try:
        title_to_emb = load_activity_embeddings()
        if not title_to_emb:
            return []

        activities, activity_map = load_activities()
        kg = load_kg_edges()
        embed_dim = next(iter(title_to_emb.values())).shape[0]

        # Conditionally fetch data based on the flags
        long_term_prefs = get_user_preferences(db, username) if use_long_term else {}
        recent_messages = get_recent_interactions(db, username) if use_short_term else []
        feedback = get_user_feedback_from_db(db, username) if use_feedback else {}

        # Create a vector for each signal
        feedback_vec = create_feedback_vector(feedback, title_to_emb, embed_dim)
        short_term_vec = create_short_term_intention_vector(recent_messages)

        # Build long-term vector from liked preference keywords matched to activity titles/descriptions
        liked_keywords = [c for pref_type, contents in long_term_prefs.items()
                          for c in (contents if isinstance(contents, list) else [contents])
                          if pref_type in ("like", "modality", "activity")]

        if liked_keywords:
            keyword_text = " ".join(liked_keywords)
            long_term_vec = CONTEXT_MODEL.encode(keyword_text)
        else:
            # Fall back: average all activity embeddings (neutral prior)
            long_term_vec = np.mean(list(title_to_emb.values()), axis=0)

        # --- Normalise every signal before fusing ---
        def safe_norm(v):
            n = np.linalg.norm(v)
            return v / n if n > 0 else v

        long_term_vec = safe_norm(long_term_vec)
        feedback_vec  = safe_norm(feedback_vec)  if np.linalg.norm(feedback_vec) > 0 else feedback_vec

        w_lt, w_st, w_fb = W_LONG_TERM, W_SHORT_TERM, W_FEEDBACK

        if short_term_vec is None:
            # Redistribute short-term weight to long-term
            w_lt += w_st
            w_st  = 0.0
            short_term_vec = np.zeros(embed_dim)
        else:
            short_term_vec = safe_norm(short_term_vec)

        fused_vector = w_fb * feedback_vec + w_lt * long_term_vec + w_st * short_term_vec
        fused_vector = safe_norm(fused_vector)

        # Score every activity with cosine similarity
        results = []
        for title, embedding in title_to_emb.items():
            if title not in activity_map:
                continue
            sim = float(np.dot(fused_vector, safe_norm(embedding)))
            activity_details = activity_map[title]
            results.append({
                "title": title,
                "score": round(sim, 4),
                "rationale": build_rationale(title, kg),
                "description": activity_details.get("short_description", ""),
                "visual_asset_id": activity_details.get("visual_asset_id"),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    except Exception as e:
        print(f"💥 recommend_activities error for '{username}': {e}")
        print(traceback.format_exc())
        return []