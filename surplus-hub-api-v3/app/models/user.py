from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    name = Column(String, index=True)
    profile_image_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    role = Column(String, default="user")

    trust_level = Column(Integer, default=1)
    manner_temperature = Column(Float, default=36.5)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    admin_role = Column(String, nullable=True, default=None)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def avatar_url(self):
        return self.profile_image_url
