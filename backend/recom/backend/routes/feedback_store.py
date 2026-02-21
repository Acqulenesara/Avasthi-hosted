from collections import defaultdict

feedback_store = defaultdict(dict)

def save_feedback(username: str, activity_title: str, liked: bool):
    feedback_store[username][activity_title] = liked

def get_user_feedback(username: str):
    return feedback_store.get(username, {})