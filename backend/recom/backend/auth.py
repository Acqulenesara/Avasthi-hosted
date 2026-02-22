from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from jose import jwt, JWTError
from .settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password[:72])

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # your login route

def extract_username_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return username
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
