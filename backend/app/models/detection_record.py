from sqlalchemy import Column, Integer, Boolean, DateTime
from datetime import datetime
from backend.app.db import Base

class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(Integer, primary_key=True, index=True)
    cam = Column(Integer, nullable=False)
    detected = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
