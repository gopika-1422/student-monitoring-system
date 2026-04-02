@echo off
echo.
echo ====================================================
echo    AI Smart Attendance System - Quick Start (Win)
echo ====================================================
echo.

set ROOT=%~dp0

REM ── Backend ──────────────────────────────────────────
echo [1/4] Setting up Python backend...
cd /d "%ROOT%backend"

if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
)

call venv\Scripts\activate
pip install -r requirements.txt -q

if not exist ".env" (
    copy .env.example .env
    echo Created .env from example
)

if not exist "storage\images" mkdir storage\images
if not exist "storage\embeddings" mkdir storage\embeddings
if not exist "storage\exports" mkdir storage\exports

echo [2/4] Starting backend...
start "Backend" cmd /k "cd /d %ROOT%backend && venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ── Frontend ──────────────────────────────────────────
echo [3/4] Setting up frontend...
cd /d "%ROOT%frontend"

if not exist "node_modules" (
    echo Installing npm packages...
    npm install
)

echo [4/4] Starting frontend...
start "Frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

echo.
echo ====================================================
echo   System is running!
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   Login: admin / admin123
echo.
echo   For AI chatbot:
echo   1. Install Ollama from https://ollama.ai
echo   2. Run: ollama serve
echo   3. Run: ollama pull llama3
echo ====================================================
echo.
pause
