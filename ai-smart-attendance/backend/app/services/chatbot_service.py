import httpx
import json
import logging
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.config import settings
from app.models.attendance import AttendanceRecord
from app.models.student import Student
from app.models.emotion_log import Alert

logger = logging.getLogger(__name__)


async def query_ollama(prompt: str, system_prompt: str = "") -> str:
    """Query local Ollama LLM."""
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 512,
        },
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                return f"Ollama error: {response.status_code}"
    except httpx.ConnectError:
        return "⚠️ Ollama is not running. Please start it with: `ollama serve`"
    except Exception as e:
        logger.error(f"Ollama query error: {e}")
        return f"Error querying AI assistant: {str(e)}"


async def get_context_for_query(db: AsyncSession, query: str) -> str:
    """Fetch relevant DB data based on query intent."""
    query_lower = query.lower()
    context_parts = []
    today = date.today()
    
    # Today's attendance
    if any(w in query_lower for w in ["today", "present", "attendance", "absent"]):
        result = await db.execute(
            select(
                Student.full_name,
                Student.student_id,
                AttendanceRecord.status,
                AttendanceRecord.check_in,
            ).join(AttendanceRecord, Student.id == AttendanceRecord.student_id, isouter=True)
            .where(AttendanceRecord.date == today)
            .limit(20)
        )
        rows = result.fetchall()
        if rows:
            context_parts.append(f"Today's attendance ({today}):")
            for row in rows:
                context_parts.append(f"  - {row.full_name} ({row.student_id}): {row.status}, checked in at {row.check_in}")
    
    # Last week
    if any(w in query_lower for w in ["week", "weekly", "last week"]):
        week_ago = today - timedelta(days=7)
        result = await db.execute(
            select(
                AttendanceRecord.date,
                func.count(AttendanceRecord.id).label("present"),
            ).where(AttendanceRecord.date >= week_ago)
            .group_by(AttendanceRecord.date)
            .order_by(AttendanceRecord.date)
        )
        rows = result.fetchall()
        if rows:
            context_parts.append("Weekly attendance summary:")
            for row in rows:
                context_parts.append(f"  - {row.date}: {row.present} students present")
    
    # Inactive / low attendance
    if any(w in query_lower for w in ["inactive", "absent", "missing", "low"]):
        result = await db.execute(
            select(Student.full_name, Student.student_id)
            .where(Student.is_active == True)
            .limit(30)
        )
        all_students = result.fetchall()
        
        present_today = await db.execute(
            select(AttendanceRecord.student_code).where(AttendanceRecord.date == today)
        )
        present_codes = {r.student_code for r in present_today}
        
        absent = [s for s in all_students if s.student_id not in present_codes]
        if absent:
            context_parts.append(f"Absent students today ({len(absent)}):")
            for s in absent[:10]:
                context_parts.append(f"  - {s.full_name} ({s.student_id})")
    
    # Alerts
    if any(w in query_lower for w in ["alert", "warning", "issue"]):
        result = await db.execute(
            select(Alert).where(Alert.is_read == False).order_by(Alert.created_at.desc()).limit(5)
        )
        alerts = result.scalars().all()
        if alerts:
            context_parts.append("Recent unread alerts:")
            for alert in alerts:
                context_parts.append(f"  - [{alert.severity}] {alert.message}")
    
    return "\n".join(context_parts) if context_parts else "No specific data found for this query."


SYSTEM_PROMPT = """You are an intelligent AI assistant for a Smart Attendance & Classroom Monitoring System.
You help teachers and administrators understand attendance patterns, student behavior, and classroom analytics.
You have access to real-time attendance data, emotion logs, and alert information.
Be concise, helpful, and data-driven in your responses.
When asked about specific students or classes, use the provided context data.
Format your response clearly and professionally."""


async def chat_with_assistant(db: AsyncSession, user_message: str, history: list = None) -> str:
    """Main chat function combining DB context with Ollama."""
    context = await get_context_for_query(db, user_message)
    
    full_prompt = f"""Current date: {date.today()}

Relevant data from the attendance system:
{context}

User question: {user_message}

Please provide a helpful, accurate response based on the data above."""
    
    if history:
        history_text = "\n".join([
            f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}"
            for h in history[-6:]
        ])
        full_prompt = f"Previous conversation:\n{history_text}\n\n{full_prompt}"
    
    return await query_ollama(full_prompt, SYSTEM_PROMPT)
