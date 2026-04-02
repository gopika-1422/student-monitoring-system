from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import date, timedelta
from pydantic import BaseModel
from app.db.database import get_db
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.core.security import get_current_active_user
from app.services.attendance_service import get_attendance_stats

router = APIRouter(prefix="/attendance", tags=["Attendance"])


class AttendanceResponse(BaseModel):
    id: int
    student_code: str
    student_name: Optional[str] = None
    class_name: str
    date: date
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    duration_seconds: float
    confidence_score: float
    status: str
    is_verified: bool

    class Config:
        from_attributes = True


@router.get("/stats")
async def attendance_stats(
    class_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    return await get_attendance_stats(db, class_name)


@router.get("/")
async def list_attendance(
    class_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    student_code: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(AttendanceRecord, Student.full_name).join(
        Student, AttendanceRecord.student_id == Student.id, isouter=True
    )
    
    if class_name:
        query = query.where(AttendanceRecord.class_name == class_name)
    if start_date:
        query = query.where(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.where(AttendanceRecord.date <= end_date)
    if student_code:
        query = query.where(AttendanceRecord.student_code == student_code)
    
    query = query.order_by(AttendanceRecord.date.desc(), AttendanceRecord.check_in.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    records = []
    for record, student_name in rows:
        r = {
            "id": record.id,
            "student_code": record.student_code,
            "student_name": student_name,
            "class_name": record.class_name,
            "date": str(record.date),
            "check_in": str(record.check_in) if record.check_in else None,
            "check_out": str(record.check_out) if record.check_out else None,
            "duration_seconds": record.duration_seconds or 0,
            "confidence_score": record.confidence_score or 0,
            "status": record.status,
            "is_verified": record.is_verified,
        }
        records.append(r)
    
    return {"records": records, "total": len(records)}


@router.get("/by-student/{student_code}")
async def student_attendance_history(
    student_code: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = date.today() - timedelta(days=days)
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            and_(
                AttendanceRecord.student_code == student_code,
                AttendanceRecord.date >= start,
            )
        )
        .order_by(AttendanceRecord.date.desc())
    )
    records = result.scalars().all()
    
    total_days = days
    present_days = len(records)
    percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    return {
        "student_code": student_code,
        "total_days": total_days,
        "present_days": present_days,
        "attendance_percentage": round(percentage, 2),
        "records": [
            {
                "date": str(r.date),
                "status": r.status,
                "check_in": str(r.check_in) if r.check_in else None,
                "check_out": str(r.check_out) if r.check_out else None,
                "duration_minutes": round((r.duration_seconds or 0) / 60, 1),
            }
            for r in records
        ],
    }


@router.get("/top-students")
async def top_students(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            AttendanceRecord.student_code,
            Student.full_name,
            func.count(AttendanceRecord.id).label("present_count"),
        )
        .join(Student, AttendanceRecord.student_id == Student.id, isouter=True)
        .where(AttendanceRecord.date >= start)
        .group_by(AttendanceRecord.student_code, Student.full_name)
        .order_by(func.count(AttendanceRecord.id).desc())
        .limit(limit)
    )
    rows = result.fetchall()
    return {
        "students": [
            {
                "student_code": r.student_code,
                "full_name": r.full_name,
                "present_count": r.present_count,
                "attendance_rate": round(r.present_count / days * 100, 1),
            }
            for r in rows
        ]
    }


@router.get("/low-attendance-alerts")
async def low_attendance_alerts(
    threshold: float = Query(75.0, ge=0, le=100),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = date.today() - timedelta(days=days)
    
    # Get all students
    students_result = await db.execute(select(Student).where(Student.is_active == True))
    all_students = students_result.scalars().all()
    
    alerts = []
    for student in all_students:
        count_result = await db.execute(
            select(func.count(AttendanceRecord.id)).where(
                and_(
                    AttendanceRecord.student_code == student.student_id,
                    AttendanceRecord.date >= start,
                )
            )
        )
        present_count = count_result.scalar() or 0
        rate = (present_count / days * 100)
        
        if rate < threshold:
            alerts.append({
                "student_code": student.student_id,
                "full_name": student.full_name,
                "attendance_rate": round(rate, 2),
                "present_days": present_count,
                "total_days": days,
            })
    
    alerts.sort(key=lambda x: x["attendance_rate"])
    return {"alerts": alerts}
