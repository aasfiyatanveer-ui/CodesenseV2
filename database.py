"""
database.py — CodeSense V2
SQLite with XP, badges, streaks, multi-language reviews.
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Float,
    Text, DateTime, Boolean, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./codesense_v2.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, index=True)
    email         = Column(String, unique=True)
    hashed_password = Column(String)
    role          = Column(String, default="student")   # student / professor
    full_name     = Column(String, default="")
    avatar_color  = Column(String, default="#6366f1")   # for UI avatar
    # Gamification
    xp            = Column(Integer, default=0)
    badges        = Column(Text, default="[]")          # JSON list of badge keys
    # Stats counters
    review_count  = Column(Integer, default=0)
    fix_count     = Column(Integer, default=0)
    enhance_count = Column(Integer, default=0)
    ask_count     = Column(Integer, default=0)
    excellent_count = Column(Integer, default=0)
    java_count    = Column(Integer, default=0)
    js_count      = Column(Integer, default=0)
    c_count       = Column(Integer, default=0)
    python_count  = Column(Integer, default=0)
    created_at    = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"
    id              = Column(Integer, primary_key=True, index=True)
    student_id      = Column(String, index=True)
    username        = Column(String, index=True)
    code_snippet    = Column(Text)
    language        = Column(String, default="python")
    ml_grade        = Column(String)
    quality_score   = Column(Integer)
    confidence      = Column(Float)
    time_complexity = Column(String)
    space_complexity = Column(String)
    pylint_issues   = Column(Text, default="[]")
    xp_earned       = Column(Integer, default=0)
    reviewed_at     = Column(DateTime, default=datetime.utcnow)


class FixHistory(Base):
    __tablename__ = "fix_history"
    id           = Column(Integer, primary_key=True)
    username     = Column(String, index=True)
    language     = Column(String)
    fixes_count  = Column(Integer, default=0)
    xp_earned    = Column(Integer, default=0)
    fixed_at     = Column(DateTime, default=datetime.utcnow)


class AskHistory(Base):
    __tablename__ = "ask_history"
    id         = Column(Integer, primary_key=True)
    username   = Column(String, index=True)
    prompt     = Column(Text)
    source     = Column(String)  # groq / ollama / local_kb
    xp_earned  = Column(Integer, default=0)
    asked_at   = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
