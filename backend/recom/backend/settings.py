from pydantic import BaseModel
import os
from dotenv import load_dotenv

# override=False means real environment variables (set by Render) always win over .env
load_dotenv(override=False)

class Settings(BaseModel):
    SECRET_KEY: str
    POSTGRES_URL: str
    OPENAI_API_KEY: str | None = None
    PINECONE_API_KEY: str | None = None
    PINECONE_REGION: str | None = None
    YOUTUBE_API_KEY: str | None = None

def get_settings() -> Settings:
    try:
        return Settings(
            SECRET_KEY=os.getenv("SECRET_KEY", ""),
            POSTGRES_URL=os.getenv("POSTGRES_URL", ""),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
            PINECONE_API_KEY=os.getenv("PINECONE_API_KEY"),
            PINECONE_REGION=os.getenv("PINECONE_REGION"),
            YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY"),
        )
    except Exception as e:
        raise RuntimeError(f"Invalid environment configuration: {e}")