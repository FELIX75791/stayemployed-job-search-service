from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    location: str

class Job(JobCreate):
    id: int

    class Config:
        orm_mode = True
