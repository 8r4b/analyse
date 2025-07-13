from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RecordingSession(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    transcript = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)  # List of suggestions stored as JSON
    created_at = Column(DateTime, nullable=False)
