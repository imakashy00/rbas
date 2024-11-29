from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 

load_dotenv()

POSTGRESQL_DATABASE_URL = os.getenv('POSTGRESQL_DATABASE_URL')

engine = create_engine(POSTGRESQL_DATABASE_URL,echo=False)

SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind = engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()