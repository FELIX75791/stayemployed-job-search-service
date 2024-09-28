# create_tables.py
from app.database import engine, Base
from app.models import Job  # Import your models here

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run the script
import asyncio
asyncio.run(main())

