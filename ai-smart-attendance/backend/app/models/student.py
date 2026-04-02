from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, LargeBinary
from sqlalchemy.sql import func
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    class_name = Column(String, nullable=False, default="Default")
    section = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    face_embedding = Column(Text, nullable=True)  # JSON-encoded numpy array
    is_active = Column(Boolean, default=True)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
