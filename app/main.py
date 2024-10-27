# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # Import select from sqlalchemy.future
from app.database import get_db
from app.models import Job
from app.schemas import JobCreate
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Job Search Service!"}




