"""
RetailWise AI — Database Engine + Session Factory
SQLite via SQLAlchemy 2.0
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base  # noqa: F401 — re-exported for Alembic / seed use

load_dotenv()

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "sqlite:///./database/retailwise.db"
)

# SQLite needs check_same_thread=False for FastAPI's async request handling
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # set True locally to debug SQL queries
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session, always closes on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
