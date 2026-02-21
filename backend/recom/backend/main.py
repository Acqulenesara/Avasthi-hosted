from fastapi import FastAPI, HTTPException, Form
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, User, Feedback
from .schemas import UserRegister, QueryPayload, FeedbackRequest
from .auth import get_user, get_password_hash, authenticate_user
from .settings import get_settings
from .routes.recommendations import router as rec_router
from .routes.users import router as users_router
from .routes.feedback import router as feedback_router
from .routes.history import router as history_router
from datetime import datetime
# Add these imports at the top of your main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Wellness CRS with KG + DCL")

# Create tables
Base.metadata.create_all(bind=engine)


app.add_middleware(
CORSMiddleware,
allow_origins=["http://localhost:3000"],  # The origin of your React app
allow_credentials=True,
allow_methods=[""],
allow_headers=[""],
)


# Core endpoints
@app.post("/register")
def register_user(user: UserRegister):
    db = SessionLocal()
    if get_user(db, user.username):
        db.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.close()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = authenticate_user(db, username, password)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "username": user.username,
        "email": user.email,
        "preferences_collected": user.preferences_collected
    }

# Routers
app.include_router(rec_router)
app.include_router(users_router)
app.include_router(feedback_router)
app.include_router(history_router)