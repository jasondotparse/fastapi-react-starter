from sqlalchemy import Column, Integer, String, Text, Boolean
from .database import Base
import datetime
from sqlalchemy import DateTime

class UserModel(Base):
    """Database model for storing user info."""
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    age = Column(Integer)
