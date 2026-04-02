import os
import json
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from pydantic import BaseModel
from app.db.database import get_db
from app.models.student import Student
from app.core.security import get_current_active_user
from app.core.config import settings
from app.services.face_service import extract_embedding_from_image_bytes, save_embedding

router = APIRouter(prefix="/students", tags=["Students"])


class StudentCreate(BaseModel):
    student_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    class_name: str = "Default"
    section: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    class_name: str
    section: Optional[str]
    photo_path: Optional[str]
    is_active: bool
    has_face_data: bool = False

    class Config:
        from_attributes = True


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    class_name: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Student).where(Student.is_active == True)
    if class_name:
        query = query.where(Student.class_name == class_name)
    if search:
        query = query.where(
            Student.full_name.ilike(f"%{search}%") | 
            Student.student_id.ilike(f"%{search}%")
        )
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()
    
    response = []
    for s in students:
        r = StudentResponse.model_validate(s)
        r.has_face_data = s.face_embedding is not None
        response.append(r)
    return response


@router.get("/count")
async def count_students(db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(func.count(Student.id)).where(Student.is_active == True))
    return {"count": result.scalar() or 0}


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(select(Student).where(Student.student_id == student_data.student_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    student = Student(**student_data.model_dump())
    db.add(student)
    await db.flush()
    r = StudentResponse.model_validate(student)
    r.has_face_data = False
    return r


@router.post("/{student_id}/photo")
async def upload_student_photo(
    student_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Save image
    img_path = os.path.join(settings.IMAGES_PATH, f"{student_id}.jpg")
    contents = await file.read()
    with open(img_path, "wb") as f:
        f.write(contents)
    
    # Extract embedding
    embedding = extract_embedding_from_image_bytes(contents)
    if embedding:
        student.face_embedding = json.dumps(embedding)
        student.photo_path = img_path
        save_embedding(student_id, embedding, settings.EMBEDDINGS_PATH)
        return {"message": "Photo uploaded and face data extracted successfully", "has_face_data": True}
    else:
        student.photo_path = img_path
        return {"message": "Photo uploaded but no face detected", "has_face_data": False}


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    r = StudentResponse.model_validate(student)
    r.has_face_data = student.face_embedding is not None
    return r


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for key, value in student_data.model_dump().items():
        setattr(student, key, value)
    
    r = StudentResponse.model_validate(student)
    r.has_face_data = student.face_embedding is not None
    return r


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_active = False
    return {"message": "Student deactivated"}


@router.get("/classes/list")
async def list_classes(db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(Student.class_name).distinct())
    classes = [r[0] for r in result.fetchall()]
    return {"classes": classes}
