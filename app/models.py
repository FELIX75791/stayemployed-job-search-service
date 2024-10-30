from sqlalchemy import Column, Integer, String
from app.database import Base
from pydantic import BaseModel

BASE_URL = "http://3.213.98.62:8080"
class Link(BaseModel):
    rel: str
    href: str


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Specify a length for VARCHAR
    location = Column(String(255), nullable=False)  # Specify a length for VARCHAR
    # Add other fields with lengths as necessary


