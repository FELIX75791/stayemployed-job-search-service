#Job Search Microservice



##Overview

This repo contains the reference implementation for the **job-search microservice** in project **stayemployeed**

## Installation

Create a virtual environment and install the dependencies according to requirements.txt. The microservice has been deployed on AWS, with data stored in RDS, with job information fetched from Careerjet API

##Quick-Start

**If you need to run the microservice with notification function, please contact the author with the email API key and domain.**

'''uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload'''

##### ##File Descriptions

1. **`database.py`**

   - Handles database configuration using SQLAlchemy.
   - Provides:
     - Asynchronous and synchronous database sessions (`get_db_async`, `get_db_sync`).
     - A declarative base (`Base`) for defining ORM models.
   - **Database URL** is defined for connecting to a MySQL database hosted on AWS RDS.

2. **`main.py`**

   - Entry point for the application.
   - Features:
     - Middleware for logging request details.
     - Integration with Mailgun for sending email notifications.
   - Exposes a root endpoint (`/`) to verify service availability.

3. **`routes.py`**

   - Defines application routes for:
     - Fetching jobs from Careerjet (`/fetch-jobs`).
     - Viewing jobs on the homepage (`/jobs/home`).
     - Managing job resources (CRUD operations on `/jobs` endpoints).
     - Fetching user emails from a profile microservice (`/get-user-emails`).
   - Integrates email notifications for new job postings.

4. **`models.py`**

   - Defines the database model for 

     ```
     Job
     ```

      with fields:

     - `id`: Primary key.
     - `title`: Job title.
     - `location`: Job location.

   - Includes a `Link` schema for API hypermedia representation.
