# create_tables.py
from models import Base
from database import engine

Base.metadata.drop_all(bind=engine)   # drops all tables
Base.metadata.create_all(bind=engine) # recreates tables
print("Tables recreated successfully!") 




