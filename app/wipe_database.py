# somewhere in your codebase, e.g. scripts/recreate_db.py

import asyncio
from database import engine     # your AsyncEngine
from models import Base         # your DeclarativeBase

async def recreate():
    # connect and drop+create within a transaction
    async with engine.begin() as conn:
        # Drops all tables defined on Base.metadata
        await conn.run_sync(Base.metadata.drop_all)
        # Recreates them from your current models
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(recreate())
    print("✔️  Database schema recreated.")

