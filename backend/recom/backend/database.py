from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import get_settings
import os

settings = get_settings()

if not settings.POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL is required")

# Use POSTGRES_URL from environment, replacing asyncpg driver with psycopg2
# (SQLAlchemy sync engine needs psycopg2, not asyncpg)
_db_url = (settings.POSTGRES_URL
           .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
           .replace("postgresql://", "postgresql+psycopg2://")
           .split("?")[0])  # strip ?sslmode=require for psycopg2

# Create the SQLAlchemy engine
engine = create_engine(_db_url)

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
