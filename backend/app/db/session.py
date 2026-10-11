from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import db_settings

engine = create_engine(
    db_settings.url,
    pool_pre_ping = True,
)

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    expire_on_commit = False,
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

