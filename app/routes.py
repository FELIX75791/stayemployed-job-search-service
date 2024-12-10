from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db_sync, get_db_async
from app.models import Job, Link, BASE_URL
from app.schemas import JobCreate
import requests
from app.main import send_email
from careerjet_api import CareerjetAPIClient
from pydantic import BaseModel

router = APIRouter()
class CareerjetRequest(BaseModel):
    location: str
    keywords: str
    sort: str
    contract_period: str
    purpose: str


@router.post("/fetch-jobs")
async def get_jobs(request: Request, item: CareerjetRequest, db: Session = Depends(get_db_sync)):
    cj  =  CareerjetAPIClient("en_US")
    user_ip = request.client.host
    full_url = str(request.url)

    location = item.location
    keywords = item.keywords
    sort = item.sort
    contract_period = item.contract_period
    purpose = item.purpose

    available_jobs = cj.search({
      'location': location,                 
      'keywords': keywords,
      'sort': sort,   
      'contractperiod': contract_period,             
      'affid': '213e213hd12344552',
      'user_ip': user_ip,
      'url': full_url,
      'user_agent': 'Mozilla/5.0',
    })

    job_list = available_jobs["jobs"]
    save_jobs = available_jobs["jobs"][:10]
    
    if len(available_jobs) == 0:
        return {"message": "No job found."}
    
    if purpose == "dashboard":
        job_list = job_list[:10]

    # for job_data in save_jobs:
    #   # get job information from api
    #   job_title = job_data.get("title")
    #   job_location = job_data.get("locations")
    #   # store to db
    #   new_job = Job(title=job_title, location=job_location)
    #   db.add(new_job)
    #   db.commit()
    #   db.refresh(new_job)

    return {
            "message": "Jobs fetched and saved successfully",
            "count": len(job_list),
            "job_list": job_list,
            }


@router.get("/jobs/home")
def show_jobs_homepage(db: Session = Depends(get_db_sync)):
    jobs = db.query(Job).all()

    job_list = [
        {
            "title": job.title,
            "location": job.location
        } for job in jobs
    ]

    return {"jobs": job_list}


@router.post("/jobs/fetch")
def fetch_jobs(db: Session = Depends(get_db_sync)):
    # jobs = fetch_jobs_from_linkedin()
    for job in jobs:
        new_job = Job(
            title=job.get("title", "Unknown"),
            location=job.get("location", "Unknown")
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        # Notify users
        users = ["user1@example.com", "user2@example.com"]  # Replace with actual user emails list
        for user in users:
            send_email(user, "New Job Posted", f"Check out the new job: {new_job.title} at {new_job.location}")

    return {"message": "Jobs fetched and users notified successfully"}

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



