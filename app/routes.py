from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db_sync, get_db_async
from app.models import Job, Link, BASE_URL
from app.schemas import JobCreate
import requests
from app.main import send_email

router = APIRouter()
LINKEDIN_API_URL = "https://api.linkedin.com/v2/jobPosts"
LINKEDIN_ACCESS_TOKEN = "linkedin_api_access_token"  # Replace with actual token


@router.post("/linkedin/fetch-jobs")
def fetch_jobs_from_linkedin(db: Session = Depends(get_db_sync)):
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    params = {
        "keywords": "Software Engineer",  # adjust keywords accordingly
        "location": "United States"  # adjust location accordingly
    }

    response = requests.get(LINKEDIN_API_URL, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {response.text}")

    jobs = response.json().get("elements", [])

    for job_data in jobs:
        # get job information from api
        job_title = job_data.get("title", "Unknown")
        job_location = job_data.get("location", "Unknown")

        # store to db
        new_job = Job(title=job_title, location=job_location)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

    return {"message": "Jobs fetched and saved successfully", "count": len(jobs)}
@router.get("/linkedin/auth")
def linkedin_auth():
    client_id = "869sr8v75oww0e"  # Replace with your LinkedIn app's Client ID
    redirect_uri = "http://3.213.98.62:8080/linkedin/callback"
    state = "8T0dAfxEXzf4xqbKSCum_Q"  # Replace with a secure random string
    scope = "r_liteprofile r_emailaddress"  # Add scopes required for your app
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope={scope}"
    )
    return {"authorization_url": auth_url}


@router.get("/linkedin/callback")
def linkedin_callback(code: str, state: str):
    client_id = "869sr8v75oww0e"  # Replace with your LinkedIn app's Client ID
    client_secret = "WPL_AP1.V3ffAiQmxuDeLW4n.MoIjIA==" # Replace with your LinkedIn app's Client Secret"
    redirect_uri = "http://3.213.98.62:8080/linkedin/callback"

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return {"access_token": access_token}
    else:
        return {"error": response.text}, response.status_code

@router.post("/linkedin/fetch-jobs")
def fetch_jobs_from_linkedin(db: Session = Depends(get_db_sync)):
    """
    从 LinkedIn API 获取职位信息并保存到数据库
    """
    LINKEDIN_ACCESS_TOKEN = "your_access_token"  # 替换为你的 LinkedIn Access Token
    LINKEDIN_JOB_API_URL = "https://api.linkedin.com/v2/jobPosts"

    # 请求头
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # 调用 LinkedIn API
    response = requests.get(LINKEDIN_JOB_API_URL, headers=headers)

    if response.status_code == 200:
        jobs = response.json()  # 根据 API 返回的格式调整解析逻辑
        for job in jobs.get("elements", []):  # 假设职位信息在 "elements" 键中
            # 提取职位信息字段
            title = job.get("title", {}).get("text", "Unknown Title")
            location = job.get("location", {}).get("city", "Unknown Location")

            # 保存到数据库
            new_job = Job(title=title, location=location)
            db.add(new_job)

        db.commit()
        return {"message": "Jobs fetched and saved successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


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
    jobs = fetch_jobs_from_linkedin()
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



