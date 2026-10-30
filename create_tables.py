"""Create any missing database tables without deleting existing data."""

from models import Base
from database import engine

Base.metadata.create_all(bind=engine)
print("Database tables are ready.")




