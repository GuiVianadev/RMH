from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, pool_pre_ping=True)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()