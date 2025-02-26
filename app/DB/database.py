"""
Database engine and session management for PostgreSQL using SQLAlchemy.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT


# PostgreSQL connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the engine
engine = create_engine(DATABASE_URL, echo=False, future=True)

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
