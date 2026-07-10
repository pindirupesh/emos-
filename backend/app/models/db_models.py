from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# Users table – stores everyone who signs up
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  # We'll store plain text for hackathon speed
    created_at = Column(DateTime, default=datetime.utcnow)

# Meetings table – stores each uploaded meeting transcript and its AI summary
class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    transcript_text = Column(Text, nullable=False)  # The raw uploaded text
    summary = Column(Text)                          # AI-generated summary
    structured_data = Column(JSON)                  # Full AI extraction (decisions, actions, etc.)
    meeting_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

# Commitments table – the heart of EMOS! Stores every commitment made in meetings
class Commitment(Base):
    __tablename__ = "commitments"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    task = Column(String, nullable=False)           # e.g., "Finish the dashboard"
    owner = Column(String, nullable=False)          # e.g., "John"
    deadline = Column(DateTime)                     # When it's due (nullable)
    priority = Column(String, default="Medium")     # High, Medium, Low
    status = Column(String, default="Pending")      # Pending, Done, Overdue
    dependencies = Column(JSON, default=[])         # List of commitment IDs this blocks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)