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

# автоматически создаём все таблицы, если их нет
Base.metadata.create_all(bind=engine)
