from fastapi import APIRouter, Form
from ..database import SessionLocal
from ..auth import get_user

router = APIRouter()

@router.post("/profile")
def get_profile(username: str = Form(...)):
    db = SessionLocal()
    user = get_user(db, username)
    db.close()
    if not user:
        return {"error": "User not found"}
    return {
        "username": user.username,
        "email": user.email,
        "preferences_collected": user.preferences_collected
    }