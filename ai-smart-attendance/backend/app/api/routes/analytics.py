import io
import csv
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import date, timedelta
from app.db.database import get_db
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.models.emotion_log import EmotionLog, Alert
from app.core.security import get_current_active_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Total students
    total_students = (await db.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalar() or 0

    # Today present
    today_present = (await db.execute(
        select(func.count(AttendanceRecord.id)).where(AttendanceRecord.date == today)
    )).scalar() or 0

    # Weekly avg
    weekly_counts = await db.execute(
        select(func.count(AttendanceRecord.id))
        .where(AttendanceRecord.date >= week_ago)
        .group_by(AttendanceRecord.date)
    )
    weekly_vals = [r[0] for r in weekly_counts.fetchall()]
    weekly_avg = sum(weekly_vals) / len(weekly_vals) if weekly_vals else 0

    # Monthly avg
    monthly_counts = await db.execute(
        select(func.count(AttendanceRecord.id))
        .where(AttendanceRecord.date >= month_ago)
        .group_by(AttendanceRecord.date)
    )
    monthly_vals = [r[0] for r in monthly_counts.fetchall()]
    monthly_avg = sum(monthly_vals) / len(monthly_vals) if monthly_vals else 0

    # Unread alerts
    unread_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.is_read == False)
    )).scalar() or 0

    # Emotion distribution (last 7 days)
    emotion_result = await db.execute(
        select(EmotionLog.emotion, func.count(EmotionLog.id).label("count"))
        .where(EmotionLog.timestamp >= week_ago)
        .group_by(EmotionLog.emotion)
        .order_by(func.count(EmotionLog.id).desc())
    )
    emotion_data = [{"emotion": r.emotion, "count": r.count} for r in emotion_result]

    # Attention rate (last 7 days)
    total_logs = (await db.execute(
        select(func.count(EmotionLog.id)).where(EmotionLog.timestamp >= week_ago)
    )).scalar() or 0
    attentive_logs = (await db.execute(
        select(func.count(EmotionLog.id)).where(
            and_(EmotionLog.timestamp >= week_ago, EmotionLog.is_attentive == True)
        )
    )).scalar() or 0
    attention_rate = (attentive_logs / total_logs * 100) if total_logs > 0 else 0

    return {
        "total_students": total_students,
        "today_present": today_present,
        "today_absent": max(0, total_students - today_present),
        "attendance_rate_today": round(today_present / total_students * 100, 1) if total_students else 0,
        "weekly_avg": round(weekly_avg, 1),
        "monthly_avg": round(monthly_avg, 1),
        "unread_alerts": unread_alerts,
        "emotion_distribution": emotion_data,
        "attention_rate": round(attention_rate, 1),
    }


@router.get("/daily-trend")
async def daily_trend(
    days: int = Query(30, ge=7, le=90),
    class_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = date.today() - timedelta(days=days)
    query = (
        select(AttendanceRecord.date, func.count(AttendanceRecord.id).label("present"))
        .where(AttendanceRecord.date >= start)
    )
    if class_name:
        query = query.where(AttendanceRecord.class_name == class_name)
    query = query.group_by(AttendanceRecord.date).order_by(AttendanceRecord.date)
    result = await db.execute(query)
    rows = result.fetchall()

    # Fill in zeros for missing days
    data = {str(r.date): r.present for r in rows}
    trend = []
    for i in range(days):
        d = str(start + timedelta(days=i))
        trend.append({"date": d, "present": data.get(d, 0)})

    return {"trend": trend}


@router.get("/emotion-trend")
async def emotion_trend(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(EmotionLog.timestamp).label("day"),
            EmotionLog.emotion,
            func.count(EmotionLog.id).label("count"),
        )
        .where(EmotionLog.timestamp >= start)
        .group_by(func.date(EmotionLog.timestamp), EmotionLog.emotion)
        .order_by(func.date(EmotionLog.timestamp))
    )
    rows = result.fetchall()
    return {"data": [{"date": str(r.day), "emotion": r.emotion, "count": r.count} for r in rows]}


@router.get("/alerts")
async def get_alerts(
    unread_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    if unread_only:
        query = query.where(Alert.is_read == False)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return {
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type,
                "message": a.message,
                "severity": a.severity,
                "is_read": a.is_read,
                "student_code": a.student_code,
                "created_at": str(a.created_at),
            }
            for a in alerts
        ]
    }


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    from sqlalchemy import update
    await db.execute(update(Alert).where(Alert.id == alert_id).values(is_read=True))
    return {"message": "Alert marked as read"}


@router.get("/export/csv")
async def export_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    class_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(AttendanceRecord, Student.full_name).join(
        Student, AttendanceRecord.student_id == Student.id, isouter=True
    )
    if start_date:
        query = query.where(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.where(AttendanceRecord.date <= end_date)
    if class_name:
        query = query.where(AttendanceRecord.class_name == class_name)
    query = query.order_by(AttendanceRecord.date.desc())

    result = await db.execute(query)
    rows = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Student ID", "Student Name", "Class", "Status",
                     "Check In", "Check Out", "Duration (min)", "Confidence"])
    for record, name in rows:
        writer.writerow([
            record.date,
            record.student_code,
            name or "",
            record.class_name,
            record.status,
            record.check_in,
            record.check_out,
            round((record.duration_seconds or 0) / 60, 1),
            round(record.confidence_score or 0, 3),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"},
    )
