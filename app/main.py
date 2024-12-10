# Gmail API Integration
import requests
from dotenv import load_dotenv
import os
import base64
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from the .env file
load_dotenv()

# Fetch Mailgun credentials from environment variables
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
    raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN must be set in the .env file.")

def send_email(to, subject, body):
    """
    Sends an email using Mailgun API.

    Parameters:
        to (str): Recipient's email address.
        subject (str): Subject of the email.
        body (str): Body content of the email.
    """
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    MAILGUN_BASE_URL = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}"

    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN]):
        raise ValueError("Mailgun API key and domain must be set as environment variables.")

    response = requests.post(
        f"{MAILGUN_BASE_URL}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"jobsearch <mailgun@{MAILGUN_DOMAIN}>",
            "to": to,
            "subject": subject,
            "text": body
        }
    )

    if response.status_code == 200:
        print(f"Email sent successfully to {to}")
    else:
        print(f"Failed to send email to {to}: {response.status_code} - {response.text}")
        response.raise_for_status()



from fastapi import FastAPI,Request
from app.routes import router  # Import the router from routes.py
from starlette.middleware.base import BaseHTTPMiddleware
import time
app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        start_time = time.time()
        print(f"Request: {request.method} {request.url}")

        # Process request and get response
        response = await call_next(request)

        # Calculate and log response time
        process_time = time.time() - start_time
        print(f"Completed in {process_time:.4f} seconds")

        return response

# Add middleware to the FastAPI app
app.add_middleware(LoggingMiddleware)
# Register the router for job-related routes
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Job Search Service!"}





