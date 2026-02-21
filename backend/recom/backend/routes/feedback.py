from fastapi import APIRouter
from ..database import SessionLocal
from ..models import Feedback
from ..schemas import FeedbackRequest

router = APIRouter()

@router.post("/feedback")
def save_feedback(feedback: FeedbackRequest):
    db = SessionLocal()
    new_feedback = Feedback(
        username=feedback.username,
        activity_title=feedback.activity_title,
        liked=feedback.liked
    )
    db.add(new_feedback)
    db.commit()
    db.close()
    return {"message": "Feedback saved"}