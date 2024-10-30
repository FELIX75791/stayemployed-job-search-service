from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db_sync, get_db_async
from app.models import Job, Link, BASE_URL
from app.schemas import JobCreate
router = APIRouter()


# Create a job (sync)
@router.post("/jobs/", status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db_sync)):
    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "job_id": new_job.id,
        "title": new_job.title,
        "location": new_job.location,
        "links": [
            Link(rel="self", href=f"{BASE_URL}/jobs/{new_job.id}").dict(),
            Link(rel="apply", href=f"{BASE_URL}/application-management/apply/{new_job.id}").dict()
        ]
    }


# Read all jobs (async) with pagination
@router.get("/jobs/")
async def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db_async)
):
    offset = (page - 1) * page_size
    jobs = await db.execute(select(Job).offset(offset).limit(page_size))
    job_list = jobs.scalars().all()
    total_count = await db.scalar(select(func.count()).select_from(Job))
    total_pages = (total_count + page_size - 1) // page_size

    job_data = [
        {
            "job_id": job.id,
            "title": job.title,
            "location": job.location,
            "links": [
                Link(rel="self", href=f"{BASE_URL}/jobs/{job.id}").dict(),
                Link(rel="apply", href=f"{BASE_URL}/application-management/apply/{job.id}").dict()
            ]
        }
        for job in job_list
    ]

    links = [Link(rel="self", href=f"{BASE_URL}/jobs?page={page}&page_size={page_size}").dict()]
    if page > 1:
        links.append(Link(rel="previous", href=f"{BASE_URL}/jobs?page={page-1}&page_size={page_size}").dict())
    if page < total_pages:
        links.append(Link(rel="next", href=f"{BASE_URL}/jobs?page={page+1}&page_size={page_size}").dict())

    return {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "jobs": job_data,
        "links": links
    }



# Update a job by ID (sync)
@router.put("/jobs/{job_id}")
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db_sync)):
    job_to_update = db.query(Job).filter(Job.id == job_id).first()
    if job_to_update is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_to_update.title = job.title
    job_to_update.location = job.location
    db.commit()
    db.refresh(job_to_update)

    return {
        "job_id": job_to_update.id,
        "title": job_to_update.title,
        "location": job_to_update.location,
        "links": [
            Link(rel="self", href=f"{BASE_URL}/jobs/{job_id}").dict(),
            Link(rel="apply", href=f"{BASE_URL}/application-management/apply/{job_id}").dict()
        ]
    }


# Delete a job by ID (sync)
@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db_sync)):
    job_to_delete = db.query(Job).filter(Job.id == job_id).first()
    if job_to_delete is None:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job_to_delete)
    db.commit()

    return {
        "message": "Job deleted successfully",
        "links": [
            Link(rel="job_list", href=f"{BASE_URL}/jobs").dict(),
            Link(rel="create_job", href=f"{BASE_URL}/jobs").dict()
        ]
    }


# Add an endpoint to fetch a job by ID
@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_db_async)):
    job = await db.execute(select(Job).where(Job.id == job_id))
    job_data = job.scalar_one_or_none()
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    job_with_links = {
        "job_id": job_data.id,
        "title": job_data.title,
        "location": job_data.location,
        "links": [
            Link(rel="self", href=f"{BASE_URL}/jobs/{job_id}").dict(),
            Link(rel="apply", href=f"{BASE_URL}/application-management/apply/{job_id}").dict()
        ]
    }
    return job_with_links



