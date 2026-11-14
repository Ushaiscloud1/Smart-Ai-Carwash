
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Read the database connection string from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create the SQLAlchemy database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Create a factory for database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Base class for our database models
class Base(DeclarativeBase):
    pass


# Provide a database session to FastAPI endpoints
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
