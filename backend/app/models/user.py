from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    """
    User domain model representing the entity stored in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    pokemon_team = Column(ARRAY(Integer), default=[], nullable=True)
    is_active = Column(Boolean, default=True)