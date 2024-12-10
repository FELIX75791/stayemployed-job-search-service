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
import os
router = APIRouter()
USER_PROFILE_SERVICE_URL=os.getenv("USER_PROFILE_SERVICE_URL","http://44.211.146.131:8080/users/notifications-enabled")


class CareerjetRequest(BaseModel):
    location: str
    keywords: str
    sort: str
    contract_period: str
    purpose: str


@router.post("/fetch-jobs")
async def get_jobs(request: Request, item: CareerjetRequest, db: Session = Depends(get_db_sync)):
    cj = CareerjetAPIClient("en_US")
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

@router.get("/get-user-emails")
def get_user_emails():
    try:
        # 调用 user-profile 微服务的 API
        response = requests.get(USER_PROFILE_SERVICE_URL)
        response.raise_for_status()
        data = response.json()
        email_list = data
        return {"emails": email_list}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user emails: {str(e)}")

@router.post("/jobs/fetch")
async def fetch_jobs(db: AsyncSession = Depends(get_db_async)):
    # Await the result of the get_jobs function
    jobs_response = await get_jobs()
    jobs = jobs_response.get("job_list", [])  # Extract job list from the response

    for job in jobs:
        new_job = Job(
            title=job.get("title", "Unknown"),
            location=job.get("location", "Unknown")
        )
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)

        # Fetch user emails
        email_data = get_user_emails()
        email_list = email_data.get("emails", [])

        if not email_list:
            raise HTTPException(status_code=404, detail="No emails found.")

        # Send email notifications
        for user_email in email_list:
            send_email(
                user_email,
                "New Job Posted",
                f"Check out the new job: {new_job.title} at {new_job.location}"
            )

    return {"message": "Jobs fetched and notifications sent successfully"}




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

    return {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "job_list": [
            {
                "job_id": job.id,
                "title": job.title,
                "location": job.location
            }
            for job in job_list
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



