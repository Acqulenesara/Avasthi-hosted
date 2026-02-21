from collections import defaultdict
from datetime import datetime

recommendation_history = defaultdict(list)

def log_recommendation(username: str, recommendations: list):
    recommendation_history[username].append({
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations
    })

def get_recommendation_history(username: str):
    return recommendation_history.get(username, [])