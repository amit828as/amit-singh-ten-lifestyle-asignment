"""
Database engine and session management for PostgreSQL using SQLAlchemy.
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# If you want, load from .env file using dotenv
# from dotenv import load_dotenv
# load_dotenv()

# For demonstration, let's assume we have environment variables like:
# DATABASE_URL="postgresql://user:password@localhost:5432/mydatabase"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mydatabase")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True, future=True)

# SessionLocal is our session factory, each request will use a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

def get_db() -> Generator:
    """
    A FastAPI dependency that provides a transactional scope.
    Yields:
        SQLAlchemy Session: a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
