from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from app.db.database import Base


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    student_code = Column(String, nullable=False)
    emotion = Column(String, nullable=False)  # happy, neutral, sad, angry, surprise, fear, disgust
    confidence = Column(Float, default=0.0)
    is_attentive = Column(Boolean, default=True)
    head_pose_yaw = Column(Float, nullable=True)
    head_pose_pitch = Column(Float, nullable=True)
    head_pose_roll = Column(Float, nullable=True)
    session_id = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)  # absent, inactive, low_attendance
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    student_code = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    severity = Column(String, default="warning")  # info, warning, critical
    is_read = Column(Boolean, default=False)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    class_name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    total_students = Column(Integer, default=0)
    present_students = Column(Integer, default=0)
    camera_source = Column(String, default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
