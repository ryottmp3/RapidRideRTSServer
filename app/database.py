# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# load the .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Load PostgreSQL connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine — uses asyncpg for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with async_session() as session:
        yield session

