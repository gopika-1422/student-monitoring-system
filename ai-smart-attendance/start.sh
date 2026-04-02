#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   AI Smart Attendance System - Quick Start       ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Backend ──────────────────────────────────────────────
echo "▶ Setting up backend..."
cd "$ROOT/backend"

if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "  Created virtual environment"
fi

source venv/bin/activate
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  Created .env from example"
fi

mkdir -p storage/images storage/embeddings storage/exports

echo "  Starting backend on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# ── Frontend ──────────────────────────────────────────────
echo ""
echo "▶ Setting up frontend..."
cd "$ROOT/frontend"

if [ ! -d "node_modules" ]; then
  npm install -q
  echo "  Installed npm packages"
fi

echo "  Starting frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

# ── Summary ──────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   System is running!                             ║"
echo "║                                                  ║"
echo "║   Frontend:  http://localhost:5173               ║"
echo "║   Backend:   http://localhost:8000               ║"
echo "║   API Docs:  http://localhost:8000/docs          ║"
echo "║                                                  ║"
echo "║   Login: admin / admin123                        ║"
echo "║                                                  ║"
echo "║   For AI chatbot, run in another terminal:       ║"
echo "║   ollama serve && ollama pull llama3             ║"
echo "║                                                  ║"
echo "║   Press Ctrl+C to stop all services             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
