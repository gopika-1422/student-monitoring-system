import json
import uuid
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.models.emotion_log import Alert, ClassSession
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory tracking: {session_id: {student_code: {first_seen, last_seen, duration, marked}}}
_session_tracker: Dict[str, Dict] = {}


def get_or_create_session_tracker(session_id: str) -> Dict:
    if session_id not in _session_tracker:
        _session_tracker[session_id] = {}
    return _session_tracker[session_id]


def update_presence(session_id: str, student_code: str, confidence: float) -> Dict:
    """Update in-memory presence tracker and return status."""
    tracker = get_or_create_session_tracker(session_id)
    now = datetime.utcnow()
    
    if student_code not in tracker:
        tracker[student_code] = {
            "first_seen": now,
            "last_seen": now,
            "duration_seconds": 0,
            "attendance_marked": False,
            "confidence": confidence,
        }
    else:
        entry = tracker[student_code]
        entry["last_seen"] = now
        entry["duration_seconds"] = (now - entry["first_seen"]).total_seconds()
        entry["confidence"] = max(entry["confidence"], confidence)
    
    should_mark = (
        not tracker[student_code]["attendance_marked"]
        and tracker[student_code]["duration_seconds"] >= settings.MIN_PRESENCE_SECONDS
    )
    
    return {
        "student_code": student_code,
        "duration_seconds": tracker[student_code]["duration_seconds"],
        "should_mark": should_mark,
        "confidence": tracker[student_code]["confidence"],
    }


async def mark_attendance(
    db: AsyncSession,
    student_id: int,
    student_code: str,
    class_name: str,
    confidence: float,
    session_id: str,
) -> Optional[AttendanceRecord]:
    """Mark attendance for a student, preventing duplicates."""
    today = date.today()
    
    # Check for existing record today
    result = await db.execute(
        select(AttendanceRecord).where(
            and_(
                AttendanceRecord.student_code == student_code,
                AttendanceRecord.class_name == class_name,
                AttendanceRecord.date == today,
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update check-out time
        await db.execute(
            update(AttendanceRecord)
            .where(AttendanceRecord.id == existing.id)
            .values(
                check_out=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - existing.check_in).total_seconds(),
                updated_at=datetime.utcnow(),
            )
        )
        return existing
    
    # Determine status
    now = datetime.utcnow()
    status = "present"
    if now.hour >= 9:  # Assuming class starts at 9 AM
        status = "late"
    
    record = AttendanceRecord(
        student_id=student_id,
        student_code=student_code,
        class_name=class_name,
        date=today,
        check_in=now,
        confidence_score=confidence,
        status=status,
        is_verified=True,
        session_id=session_id,
    )
    db.add(record)
    
    # Mark in memory tracker
    if session_id in _session_tracker and student_code in _session_tracker[session_id]:
        _session_tracker[session_id][student_code]["attendance_marked"] = True
    
    return record


async def get_attendance_stats(db: AsyncSession, class_name: Optional[str] = None):
    """Get attendance statistics."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    base_query = select(AttendanceRecord)
    if class_name:
        base_query = base_query.where(AttendanceRecord.class_name == class_name)
    
    # Today's count
    today_result = await db.execute(
        select(func.count(AttendanceRecord.id)).where(
            and_(
                AttendanceRecord.date == today,
                *([AttendanceRecord.class_name == class_name] if class_name else []),
            )
        )
    )
    today_count = today_result.scalar() or 0
    
    # Total students
    student_count_result = await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )
    total_students = student_count_result.scalar() or 0
    
    # Weekly attendance
    weekly_result = await db.execute(
        select(
            AttendanceRecord.date,
            func.count(AttendanceRecord.id).label("count"),
        ).where(AttendanceRecord.date >= week_ago)
        .group_by(AttendanceRecord.date)
        .order_by(AttendanceRecord.date)
    )
    weekly_data = [{"date": str(r.date), "count": r.count} for r in weekly_result]
    
    return {
        "today_present": today_count,
        "total_students": total_students,
        "today_absent": max(0, total_students - today_count),
        "attendance_rate": (today_count / total_students * 100) if total_students > 0 else 0,
        "weekly_data": weekly_data,
    }


async def create_session(
    db: AsyncSession,
    class_name: str,
    subject: str,
    teacher_id: int,
    camera_source: str = "0",
) -> ClassSession:
    """Create a new class session."""
    session_id = str(uuid.uuid4())
    session = ClassSession(
        session_id=session_id,
        class_name=class_name,
        subject=subject,
        teacher_id=teacher_id,
        camera_source=camera_source,
        is_active=True,
    )
    db.add(session)
    await db.flush()
    return session


async def end_session(db: AsyncSession, session_id: str):
    """End an active class session."""
    await db.execute(
        update(ClassSession)
        .where(ClassSession.session_id == session_id)
        .values(end_time=datetime.utcnow(), is_active=False)
    )
    # Clean up memory tracker
    if session_id in _session_tracker:
        del _session_tracker[session_id]
