from pydantic import BaseModel
from typing import List, Optional

class UserRegister(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class QueryPayload(BaseModel):
    query: str
    thread_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    username: str
    activity_title: str
    liked: bool


class RecommendationRequest(BaseModel):
    query: Optional[str] = None
    top_k: int = 5

class RecommendationItem(BaseModel):
    activity: str
    score: float
    rationale: str

class RecommendationResponse(BaseModel):
    username: str
    recommendations: List[RecommendationItem]

class PreferencesResponse(BaseModel):
    username: str
    likes: List[str]
    dislikes: List[str]