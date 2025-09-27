# For now, models.py can stay empty or just placeholder
# If you add DB later, define SQLAlchemy models here

# Example placeholder:
class User:
    pass

#signup
from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
