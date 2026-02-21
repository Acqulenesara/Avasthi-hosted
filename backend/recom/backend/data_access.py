# in backend/data_access.py

from sqlalchemy.orm import Session
from .models import UserPreference, ChatInteraction, Feedback
from typing import Dict, List

def get_user_preferences(db: Session, username: str) -> Dict[str, List[str]]:
    """
    Fetches all stored long-term preferences for a given user.

    Returns a dictionary where keys are preference types
    (e.g., 'modality', 'activity', 'environment')
    and values are lists of user-selected preferences.
    """
    prefs = (
        db.query(UserPreference)
        .filter(UserPreference.username == username)
        .all()
    )

    user_prefs: Dict[str, List[str]] = {}

    for pref in prefs:
        pref_type = pref.preference_type
        if pref_type not in user_prefs:
            user_prefs[pref_type] = []
        user_prefs[pref_type].append(pref.content)

    return user_prefs


def get_recent_interactions(db: Session, username: str, limit: int = 5) -> List[str]:
    """Fetches the text from a user's most recent queries."""
    interactions = (
        db.query(ChatInteraction)
        .filter(ChatInteraction.username == username)
        .order_by(ChatInteraction.timestamp.desc())
        .limit(limit)
        .all()
    )
    # Return just the user's messages for context
    return [i.query for i in interactions]

def get_user_feedback_from_db(db: Session, username: str) -> Dict[str, bool]:
    """
    Fetches user feedback (likes/dislikes) from the database.
    This fixes the bug of reading from the in-memory store.
    """
    feedback_items = db.query(Feedback).filter(Feedback.username == username).all()
    return {f.activity_title: f.liked for f in feedback_items}