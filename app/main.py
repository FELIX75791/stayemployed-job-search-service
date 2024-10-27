from fastapi import FastAPI
from app.routes import router  # Import the router from routes.py

app = FastAPI()

# Register the router for job-related routes
app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Job Search Service!"}





