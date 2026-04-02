import asyncio
import base64
import json
import uuid
import logging
import cv2
import numpy as np
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db, AsyncSessionLocal
from app.models.student import Student
from app.models.emotion_log import EmotionLog, Alert
from app.core.config import settings
from app.services.face_service import extract_faces, match_face, load_embeddings_cache
from app.services.emotion_service import detect_emotion_deepface, estimate_head_pose, analyze_activity
from app.services.attendance_service import update_presence, mark_attendance

router = APIRouter(prefix="/monitor", tags=["Monitoring"])
logger = logging.getLogger(__name__)

# Connected WebSocket clients
_connections: dict = {}

# Shared embeddings cache
_embeddings_cache: dict = {}
_cache_loaded = False
_prev_frame = None


async def load_embeddings():
    global _embeddings_cache, _cache_loaded
    _embeddings_cache = load_embeddings_cache(settings.EMBEDDINGS_PATH)
    _cache_loaded = True
    logger.info(f"Loaded {len(_embeddings_cache)} face embeddings")


async def process_frame(frame: np.ndarray, session_id: str) -> dict:
    """Full AI pipeline: detect → recognize → emotion → attention."""
    global _prev_frame, _embeddings_cache
    
    if not _cache_loaded:
        await load_embeddings()
    
    result = {
        "faces": [],
        "frame_number": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Face detection & recognition
    faces = extract_faces(frame)
    
    async with AsyncSessionLocal() as db:
        for face_data in faces:
            bbox = face_data.get("bbox", [])
            embedding = face_data.get("embedding")
            confidence = face_data.get("confidence", 0)
            
            student_code = None
            match_confidence = 0.0
            student_name = "Unknown"
            
            if embedding:
                student_code, match_confidence = match_face(embedding, _embeddings_cache)
                
                if student_code:
                    # Get student name
                    result_q = await db.execute(
                        select(Student).where(Student.student_id == student_code)
                    )
                    student = result_q.scalar_one_or_none()
                    if student:
                        student_name = student.full_name
                        
                        # Update presence tracker
                        presence = update_presence(session_id, student_code, match_confidence)
                        
                        # Mark attendance if threshold met
                        if presence["should_mark"]:
                            await mark_attendance(
                                db, student.id, student_code,
                                student.class_name, match_confidence, session_id
                            )
                            await db.commit()
            
            # Extract face region for emotion detection
            emotion_data = {"emotion": "neutral", "confidence": 0.5}
            head_pose = {"yaw": 0, "pitch": 0, "roll": 0, "is_attentive": True}
            
            if len(bbox) >= 4 and settings.EMOTION_DETECTION_ENABLED:
                x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                if x2 > x1 and y2 > y1:
                    face_img = frame[y1:y2, x1:x2]
                    emotion_data = detect_emotion_deepface(face_img)
                    
                    # Log emotion to DB if student recognized
                    if student_code and match_confidence > settings.FACE_RECOGNITION_THRESHOLD:
                        result_q = await db.execute(
                            select(Student).where(Student.student_id == student_code)
                        )
                        student = result_q.scalar_one_or_none()
                        if student:
                            log = EmotionLog(
                                student_id=student.id,
                                student_code=student_code,
                                emotion=emotion_data["emotion"],
                                confidence=emotion_data["confidence"],
                                is_attentive=head_pose["is_attentive"],
                                session_id=session_id,
                            )
                            db.add(log)
                            await db.commit()
            
            face_result = {
                "bbox": bbox,
                "student_code": student_code,
                "student_name": student_name,
                "recognition_confidence": match_confidence,
                "emotion": emotion_data.get("emotion", "neutral"),
                "emotion_confidence": emotion_data.get("confidence", 0),
                "is_attentive": head_pose.get("is_attentive", True),
                "head_yaw": head_pose.get("yaw", 0),
            }
            result["faces"].append(face_result)
    
    # Activity detection
    activity = analyze_activity(_prev_frame, frame)
    result["activity"] = activity
    _prev_frame = frame.copy()
    
    return result


@router.websocket("/ws/{session_id}")
async def websocket_monitor(websocket: WebSocket, session_id: str):
    await websocket.accept()
    _connections[session_id] = websocket
    frame_count = 0
    
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "frame":
                frame_count += 1
                # Skip frames for performance
                if frame_count % settings.FRAME_SKIP != 0:
                    continue
                
                # Decode base64 frame
                img_data = message.get("data", "")
                if not img_data:
                    continue
                
                try:
                    img_bytes = base64.b64decode(img_data)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        continue
                    
                    # Process frame through AI pipeline
                    analysis = await process_frame(frame, session_id)
                    
                    await websocket.send_json({
                        "type": "analysis",
                        "data": analysis,
                    })
                    
                except Exception as e:
                    logger.error(f"Frame processing error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                    })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "reload_embeddings":
                await load_embeddings()
                await websocket.send_json({
                    "type": "info",
                    "message": f"Reloaded {len(_embeddings_cache)} embeddings",
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        _connections.pop(session_id, None)


@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    from app.models.emotion_log import ClassSession
    result = await db.execute(
        select(ClassSession).where(ClassSession.is_active == True)
    )
    sessions = result.scalars().all()
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "class_name": s.class_name,
                "subject": s.subject,
                "start_time": str(s.start_time),
                "present_students": s.present_students,
            }
            for s in sessions
        ]
    }
