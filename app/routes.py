from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db_sync, get_db_async
from app.models import Job
from app.schemas import JobCreate

router = APIRouter()


# Create a job (sync)
@router.post("/jobs/", response_model=JobCreate)
def create_job(job: JobCreate, db: Session = Depends(get_db_sync)):
    new_job = Job(title=job.title, location=job.location)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


# Read all jobs (async)
@router.get("/jobs/")
async def read_jobs(db: AsyncSession = Depends(get_db_async)):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return jobs


# Update a job by ID (sync)
@router.put("/jobs/{job_id}", response_model=JobCreate)
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db_sync)):
    job_to_update = db.query(Job).filter(Job.id == job_id).first()
    if job_to_update is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_to_update.title = job.title
    job_to_update.location = job.location
    db.commit()
    db.refresh(job_to_update)
    return job_to_update


# Delete a job by ID (sync)
@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db_sync)):
    job_to_delete = db.query(Job).filter(Job.id == job_id).first()
    if job_to_delete is None:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job_to_delete)
    db.commit()
    return {"message": "Job deleted successfully"}



