from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Define the single database URL
DATABASE_URL = "mysql+aiomysql://root:13262018@jobsearch.cvna6lesyuo6.us-east-1.rds.amazonaws.com:3306/jobsearch"

# Async engine and session for async operations
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine and session for sync operations
sync_engine = create_engine(DATABASE_URL.replace("aiomysql", "pymysql"), echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

# Dependency for async session (used in async GET)
async def get_db_async():
    async with AsyncSessionLocal() as session:
        yield session

# Dependency for sync session (used in sync POST, PUT, DELETE)
def get_db_sync():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Base class for models
Base = declarative_base()



