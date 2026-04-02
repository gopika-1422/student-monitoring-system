from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.core.security import get_current_active_user
from app.services.chatbot_service import chat_with_assistant

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    history = [{"role": m.role, "content": m.content} for m in (request.history or [])]
    response = await chat_with_assistant(db, request.message, history)
    return ChatResponse(response=response, model="ollama/local")


@router.get("/health")
async def ollama_health():
    """Check if Ollama is running."""
    import httpx
    from app.core.config import settings
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if r.status_code == 200:
                data = r.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"status": "online", "models": models}
    except Exception:
        pass
    return {"status": "offline", "models": []}
