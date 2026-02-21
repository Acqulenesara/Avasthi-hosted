from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import RecommendationRequest
from ..database import SessionLocal
from ..recommendations.recommender import recommend_activities
# from ....main import get_current_username  # import auth dependency

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_recommendations(username: str, top_k: int = 8, db: Session = Depends(get_db)):
    try:
        recs = recommend_activities(db, username, top_k)
        return {"recommendations": recs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#
# # POST endpoint
# @router.post("/recommendations")
# def recommend(payload: RecommendationRequest,
#               db: Session = Depends(get_db),
#               username: str = Depends(get_current_username)):
#     recommendations = recommend_activities(
#         db=db,
#         username=username,  # always from token
#         top_k=payload.top_k
#     )
#     return {"username": username, "recommendations": recommendations}
#
# # GET endpoint
# @router.get("/recommendations")
# def get_recommendations(
#     top_k: int = Query(5, description="Number of top recommendations to return"),
#     db: Session = Depends(get_db),
#     username: str = Depends(get_current_username)
# ):
#     recommendations = recommend_activities(
#         db=db,
#         username=username,
#         top_k=top_k
#     )
#     return {"username": username, "recommendations": recommendations}
