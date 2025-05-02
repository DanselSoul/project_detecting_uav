# backend/app/models.py
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from backend.app.db import Base

class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(Integer, primary_key=True, index=True)
    cam = Column(Integer, nullable=False)
    detected = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ValidationRecord(Base):
    __tablename__ = "validation_records"
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detection_records.id"), nullable=False)
    validated = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
