# Gmail API Integration
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_email(to, subject, body):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Gmail API credentials are missing or invalid.")

    service = build("gmail", "v1", credentials=creds)
    message = {
        "raw": base64.urlsafe_b64encode(
            f"To: {to}\nSubject: {subject}\n\n{body}".encode("utf-8")
        ).decode("utf-8")
    }
    service.users().messages().send(userId="me", body=message).execute()



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

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Job Search Service!"}





