# app/schemas.py

from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    location: str

class Job(BaseModel):
    id: int
    title: str
    location: str

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility



