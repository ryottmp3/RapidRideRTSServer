# init_db.py (project root)
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)
import asyncio
from database import engine, Base
import models


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # WARNING: for development only
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())

