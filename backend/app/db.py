from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

PASSWD = "database"

DATABASE_URL = f"postgresql://postgres:{PASSWD}@localhost/uav_detecting_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from backend.app.models.user import User       
from backend.app.models.detection_record import DetectionRecord
from backend.app.models.alarm_record     import AlarmRecord  

Base.metadata.create_all(bind=engine)
