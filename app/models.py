from sqlalchemy import Column, Integer, String
from app.database import Base


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Specify a length for VARCHAR
    location = Column(String(255), nullable=False)  # Specify a length for VARCHAR
    # Add other fields with lengths as necessary


