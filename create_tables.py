# run from terminal once to create tabled
# command python create_tables.py
# or use init-db service in docker-compose
from sqlalchemy import create_engine
from models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@db:5432/VTS_BANCKEND_DB")

engine = create_engine(DATABASE_URL)


Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
