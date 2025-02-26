"""
Main entry point for the FastAPI application.
"""
import uvicorn
from fastapi import FastAPI
from app.database import engine
from app.models import Base

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Create all tables if they don't exist yet.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Booking System API", version="0.1.0")

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
