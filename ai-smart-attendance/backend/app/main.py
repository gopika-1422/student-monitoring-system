import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.core.config import settings
from app.db.database import init_db

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    # Seed default admin user
    await seed_admin()

    # Preload face embeddings
    from app.services.face_service import load_embeddings_cache
    from app.core.config import settings as cfg
    cache = load_embeddings_cache(cfg.EMBEDDINGS_PATH)
    logger.info(f"Loaded {len(cache)} face embeddings on startup.")

    yield
    # Shutdown
    logger.info("Shutting down...")


async def seed_admin():
    from app.db.database import AsyncSessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@school.edu",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            # Also add a demo teacher
            teacher = User(
                email="teacher@school.edu",
                username="teacher",
                full_name="Demo Teacher",
                hashed_password=get_password_hash("teacher123"),
                role="teacher",
                is_active=True,
            )
            db.add(teacher)
            await db.commit()
            logger.info("Seeded default admin and teacher accounts.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Smart Attendance & Classroom Monitoring System",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for stored images
os.makedirs(settings.IMAGES_PATH, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")

# Routers
from app.api.routes import auth, students, attendance, analytics, monitor, chat

app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(monitor.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
