from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import get_settings

settings = get_settings()

if not settings.POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL is required")

# Create the SQLAlchemy engine
engine = create_engine(
    "postgresql+psycopg2://postgres:1234@localhost:5432/mental_health_bot"
)

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

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://postgres:1234@localhost/mental_health_bot"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()