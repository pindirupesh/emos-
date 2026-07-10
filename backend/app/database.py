from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables, or use a default for local testing
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://emos_user:emos_pass@localhost:5432/emos_db")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory (this is what we use to talk to the DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models (tables)
Base = declarative_base()

# Dependency: This function gives each API request its own database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables (called when the server starts)
def init_db():
    Base.metadata.create_all(bind=engine)