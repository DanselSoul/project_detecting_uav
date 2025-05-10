from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, String
from datetime import datetime
from backend.app.db import Base

class DetectionRecord(Base):
    __tablename__ = "detection_records"
    id = Column(Integer, primary_key=True, index=True)
    cam = Column(Integer, nullable=False)
    track_id = Column(Integer, nullable=False)  # 🔹 Глобальный ID объекта
    detected = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.utcnow())
    is_validated = Column(Boolean, default=False)  # 🔹 Подтверждено ли

class ValidationRecord(Base):
    __tablename__ = "validation_records"
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detection_records.id"), nullable=False)
    validated = Column(Boolean, nullable=False)  # True / False
    track_id = Column(Integer, nullable=False)   # 🔹 продублированный track_id
    camera_id = Column(Integer, nullable=False)  # 🔹 дублированный cam
    decision_source = Column(String, default="operator")  # 🔹 от кого решение
    comment = Column(String, nullable=True)      # 🔹 если нужно оставить пояснение
    timestamp = Column(DateTime, default=datetime.utcnow)
