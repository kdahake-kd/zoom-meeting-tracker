from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/meetings.db")

# Ensure data directory exists
# Extract path from DATABASE_URL if it's a file path
if "sqlite" in DATABASE_URL:
    # Parse the database path
    db_path = DATABASE_URL.split("///")[-1] if "///" in DATABASE_URL else DATABASE_URL.split("//")[-1]
    if db_path.startswith("./"):
        db_path = db_path[2:]
    elif not db_path.startswith("/"):
        db_path = f"./{db_path}"
    
    # Get directory path
    db_dir = os.path.dirname(db_path)
    if db_dir:
        # Create directory if it doesn't exist
        Path(db_dir).mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Database Models
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, unique=True, index=True, nullable=False)
    topic = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    participant_count = Column(Integer, default=0)
    host_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), nullable=False)
    user_id = Column(String)
    user_name = Column(String)
    user_email = Column(String)
    join_time = Column(DateTime)
    leave_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    device = Column(String)
    ip_address = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), nullable=False)
    recording_id = Column(String, unique=True, nullable=False)
    recording_type = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    download_url = Column(Text)
    play_url = Column(Text)
    recording_start = Column(DateTime)
    recording_end = Column(DateTime)
    file_path = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    token_type = Column(String, default="Bearer")
    created_at = Column(DateTime, default=datetime.utcnow)


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Commit read-only transactions to avoid unnecessary rollbacks
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

