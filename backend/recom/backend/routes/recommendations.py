from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import RecommendationRequest
from ..database import get_db
from ..recommendations.recommender import recommend_activities
from ..auth import extract_username_from_token, oauth2_scheme

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
def get_recommendations(top_k: int = 8, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        username = extract_username_from_token(token)
        recs = recommend_activities(db, username, top_k)
        return {"recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
