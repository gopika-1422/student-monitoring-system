from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Date
from sqlalchemy.sql import func
from app.db.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    student_code = Column(String, nullable=False, index=True)
    class_name = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, default=0)
    confidence_score = Column(Float, default=0.0)
    status = Column(String, default="present")  # present, absent, late
    is_verified = Column(Boolean, default=False)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
