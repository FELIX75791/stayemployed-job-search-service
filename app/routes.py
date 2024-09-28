from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Job  # Assuming you have a Job model defined
from app.schemas import JobCreate

router = APIRouter()

@router.post("/jobs/")
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    new_job = Job(title=job.title, location=job.location)
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job
