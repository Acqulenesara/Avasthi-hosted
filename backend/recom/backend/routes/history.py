from fastapi import APIRouter
from ..routes.history_store import get_recommendation_history

router = APIRouter()

@router.get("/recommendation-history")
def recommendation_history(username: str):
    history = get_recommendation_history(username)
    return {
        "username": username,
        "history": history
    }