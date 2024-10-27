from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Job  # Assuming a Job model is defined
from app.schemas import JobCreate  # Assuming JobCreate is a schema for job creation


router = APIRouter()
#Create
@router.post("/jobs/", response_model=JobCreate)
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    new_job = Job(title=job.title, location=job.location)  # Adjust fields as per Job model
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job

#Read
@router.get("/jobs/")
async def read_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return jobs

#Update
@router.put("/jobs/{job_id}", response_model=JobCreate)
async def update_job(job_id: int, job: JobCreate, db: AsyncSession = Depends(get_db)):
    # Find the job by ID
    result = await db.execute(select(Job).where(Job.id == job_id))
    job_to_update = result.scalar_one_or_none()

    if job_to_update is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update fields
    job_to_update.title = job.title
    job_to_update.location = job.location
    await db.commit()
    await db.refresh(job_to_update)
    return job_to_update

#Delete
@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job_to_delete = result.scalar_one_or_none()

    if job_to_delete is None:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(job_to_delete)
    await db.commit()
    return {"message": "Job deleted successfully"}


