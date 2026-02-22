from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime
from .database import Base
from pydantic import BaseModel
from typing import Optional


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    activity_title = Column(String)
    liked = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('username', 'activity_title', name='uix_feedback_user_activity'),
    )

class RecommendationRequest(BaseModel):
    username: str
    top_k: int = 5
    modality: Optional[str] = None

class FeedbackRequest(BaseModel):
    activity_title: str   # username comes from JWT, not body
    liked: bool


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    preferences_collected = Column(Integer, default=0)  # 0 = no, 1 = yes


class ChatInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    query = Column(String)
    response = Column(String)
    scenario = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)  # DateTime so ORDER BY works correctly

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
