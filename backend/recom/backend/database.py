from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import get_settings
import os

settings = get_settings()

if not settings.POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL is required")

# Normalize driver: asyncpg → psycopg2 (SQLAlchemy sync needs psycopg2)
_raw_url = (settings.POSTGRES_URL
            .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            .replace("postgresql://", "postgresql+psycopg2://"))

# Detect whether the URL requires SSL (Neon always does)
_needs_ssl = "sslmode=require" in _raw_url or "neon.tech" in _raw_url

# Strip query string from URL — pass SSL via connect_args instead
_db_url = _raw_url.split("?")[0]

_connect_args = {"sslmode": "require"} if _needs_ssl else {}

# Create the SQLAlchemy engine
engine = create_engine(_db_url, connect_args=_connect_args)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Base class for ORM models
class Base(DeclarativeBase):
    pass

# Dependency function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
