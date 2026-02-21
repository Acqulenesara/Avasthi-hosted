# in recommendations/recommender.py

import numpy as np
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import traceback  # 1. Import the traceback module

from ..data_access import get_user_preferences, get_recent_interactions, get_user_feedback_from_db
from ..dcl.utils import load_activity_embeddings
from .kg import load_kg_edges
import csv
from pathlib import Path

# --- (All your helper functions like load_activities, format_rationale, etc. remain here unchanged) ---
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
W_LONG_TERM = 0.2
W_SHORT_TERM = 0.5 # Reduced from 0.5
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



import numpy as np
from sqlalchemy.orm import Session




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

        pref_modality = long_term_prefs.get("modality")
        long_term_vecs = [
            title_to_emb.get(act['title']) for act in activities
            if act.get("modality") == pref_modality and title_to_emb.get(act['title']) is not None
        ]
        long_term_vec = np.mean(long_term_vecs, axis=0) if long_term_vecs else np.zeros(embed_dim)

        # Fuse the vectors into a single user profile
        w_lt, w_st, w_fb = W_LONG_TERM, W_SHORT_TERM, W_FEEDBACK

        if short_term_vec is None:
            total_weight = w_lt + w_fb if (w_lt + w_fb) > 0 else 1
            w_lt = w_lt / total_weight
            w_fb = w_fb / total_weight
            w_st = 0
            short_term_vec = np.zeros(embed_dim)

        fused_vector = (w_fb * feedback_vec) + (w_lt * long_term_vec) + (w_st * short_term_vec)

        norm = np.linalg.norm(fused_vector)
        if norm > 0:
            fused_vector /= norm

        # Calculate similarity and rank activities
        results = []
        for title, embedding in title_to_emb.items():
            if title not in activity_map:
                continue

            item_norm = np.linalg.norm(embedding)
            sim = np.dot(fused_vector, embedding / item_norm) if item_norm > 0 else 0.0

            activity_details = activity_map[title]
            results.append({
                "title": title,
                "score": round(float(sim), 4),
                "rationale": build_rationale(title, kg),
                "description": activity_details.get("short_description", ""),
                "visual_asset_id": activity_details.get("visual_asset_id")
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    except Exception as e:
        print(f"💥 An error occurred in recommend_activities for user '{username}': {e}")
        import traceback
        print(traceback.format_exc())
        return []