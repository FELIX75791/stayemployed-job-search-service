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





