from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    User domain model representing the entity stored in the database.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    hashed_password = Column(String, nullable=False)
    pokemon_team = Column(ARRAY(Integer), default=[], nullable=True)
    is_active = Column(Boolean, default=True)

    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
