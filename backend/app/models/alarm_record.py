from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from datetime import datetime
from backend.app.db import Base

class AlarmRecord(Base):
    __tablename__ = "alarm_records"
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detection_records.id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.id"),            nullable=False)
    action       = Column(String,  nullable=False) 
    timestamp    = Column(DateTime, default=datetime.utcnow)
