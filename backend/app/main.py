from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router

# Initialize the FastAPI application instance
app = FastAPI(
    title="Backend Challenge API",
    version="1.0.0",
    description="Clean Architecture implementation with FastAPI",
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the v1 router with the global /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """
    Health check / Root endpoint.
    """
    return {"message": "API is running correctly!"}
