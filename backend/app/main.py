from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import auth, meetings, chat

# Create the FastAPI application
app = FastAPI(
    title="EMOS Backend API",
    description="Enterprise Memory Operating System - Backend",
    version="1.0.0"
)

# Allow the frontend (Next.js running on port 3000) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the route files (auth, meetings, chat)
app.include_router(auth.router)
app.include_router(meetings.router)
app.include_router(chat.router)

# When the server starts, initialize the database (create tables)
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized successfully!")

# A simple test endpoint to check if the backend is running
@app.get("/")
def root():
    return {"message": "EMOS Backend is running! 🚀"}

# Health check endpoint for Docker
@app.get("/health")
def health():
    return {"status": "healthy"}