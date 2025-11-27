import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure environment variables are loaded (works for both dev and prod setups)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the environment.")

engine = create_engine(DATABASE_URL, echo=False)

# Factory for creating new database sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
