
#signup
from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
