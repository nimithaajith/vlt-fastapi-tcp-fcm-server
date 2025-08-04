# run from terminal once to create tabled
# command python create_tables.py
from sqlalchemy import create_engine
from models import Base
import os

DATABASE_URL = "postgresql://postgres:admin123@localhost/VTS_BANCKEND_DB"

engine = create_engine(DATABASE_URL)


Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
