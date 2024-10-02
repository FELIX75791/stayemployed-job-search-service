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

@app.post("/jobs/")
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    new_job = Job(title=job.title, location=job.location)
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job

@app.get("/jobs/")
async def read_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return jobs

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Job Search Service!"}




