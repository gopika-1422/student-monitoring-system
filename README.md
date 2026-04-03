# 🎓 AI Smart Attendance & Classroom Monitoring System

A **production-ready, fully local** AI-powered attendance system with real-time face recognition, emotion detection, attention tracking, and an intelligent chatbot — all running **100% on your machine** with no paid APIs or cloud dependencies.

---

## ✨ Features

### 🤖 AI Capabilities

| Feature | Technology |
|---------|-----------|
| Face Recognition | InsightFace `buffalo_sc` + cosine similarity |
| Emotion Detection | DeepFace (7 emotions) |
| Head Pose / Attention Tracking | OpenCV `solvePnP` |
| Activity Detection | Frame-difference analysis |
| AI Chatbot | Ollama (Llama 3 / Mistral) |

### 📊 Core Modules

- **Live Monitor** — WebSocket camera feed with real-time bounding-box overlays, emotion labels, and attention indicators
- **Smart Attendance** — Auto-marks after a configurable confirmed-presence window (default: 5 minutes)
- **Emotion Logging** — Per-student emotion timeline stored in the database
- **Analytics Dashboard** — Recharts-powered charts, trends, and top-student leaderboard
- **Alert System** — Configurable alerts for low attendance and inactive students
- **Export** — Download attendance records as CSV or Excel (`.xlsx`)

### 🎨 Frontend

- Glassmorphism design language with Tailwind CSS
- Dark / Light mode toggle (persisted via Zustand)
- Fully responsive (mobile + desktop)
- Smooth Framer Motion animations and loading skeletons
- Built with React 18, Vite 5, Recharts, Radix UI, and `lucide-react`

---

## 🚀 Quick Start

### Option A — One-Command Start (Recommended)

```bash
# Linux / macOS
./start.sh

# Windows
start.bat
```

The script automatically creates the Python virtual environment, installs all dependencies, copies `.env.example` → `.env` (if not present), and starts both backend and frontend in the background.

### Option B — Manual Setup

#### Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama *(optional — only needed for the AI chatbot)*

#### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env as needed (see Configuration section below)

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend

```bash
cd frontend

npm install
npm run dev
```

Open **http://localhost:5173**

#### 3. AI Chatbot (Optional)

```bash
# Install Ollama — https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in a separate terminal)
ollama pull llama3       # ~4 GB, higher quality
# OR
ollama pull mistral      # ~4 GB, slightly faster
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Interactive API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

The `docker-compose.yml` also includes commented-out service definitions for **PostgreSQL** and **Ollama** — uncomment those blocks if you want a fully containerised stack or a production-grade database.

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |

> ⚠️ **Change these passwords before any network-accessible deployment.**  
> JWT tokens expire after **24 hours** by default (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`).

---

## ⚙️ Configuration (`.env`)

```env
# App
SECRET_KEY=change-this-secret-key-in-production-32chars
DEBUG=true

# Database — SQLite by default; swap for PostgreSQL in production
DATABASE_URL=sqlite+aiosqlite:///./attendance.db

# CORS — comma-separated list of allowed origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# AI pipeline
FACE_RECOGNITION_THRESHOLD=0.6   # 0–1; higher = stricter matching
EMOTION_DETECTION_ENABLED=true
ATTENTION_TRACKING_ENABLED=true
FRAME_SKIP=3                      # Process every Nth frame (higher = less CPU)
MIN_PRESENCE_SECONDS=300          # Seconds before attendance is marked (default 5 min)

# Ollama chatbot
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Storage paths (relative to backend/)
STORAGE_PATH=./storage
IMAGES_PATH=./storage/images
EMBEDDINGS_PATH=./storage/embeddings
EXPORTS_PATH=./storage/exports
```

---

## 📂 Project Structure

```
ai-smart-attendance/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py           # JWT login & /me endpoint
│   │   │   ├── students.py       # Student CRUD + photo upload
│   │   │   ├── attendance.py     # Attendance records & today's stats
│   │   │   ├── analytics.py      # Overview, alerts, CSV/Excel export
│   │   │   ├── monitor.py        # WebSocket AI pipeline
│   │   │   └── chat.py           # Ollama chatbot proxy
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic-settings config
│   │   │   └── security.py       # JWT + bcrypt helpers
│   │   ├── db/
│   │   │   └── database.py       # SQLAlchemy async engine + session
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── student.py
│   │   │   ├── attendance.py
│   │   │   └── emotion_log.py
│   │   ├── services/
│   │   │   ├── face_service.py        # InsightFace recognition + embedding cache
│   │   │   ├── emotion_service.py     # DeepFace + head-pose attention
│   │   │   ├── attendance_service.py  # Presence tracking logic
│   │   │   └── chatbot_service.py     # Ollama HTTP client
│   │   └── main.py               # FastAPI app, CORS, lifespan, seeding
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx     # Stats + charts
│   │   │   ├── StudentsPage.jsx      # CRUD + webcam photo upload
│   │   │   ├── LiveMonitorPage.jsx   # WebSocket camera feed
│   │   │   ├── AttendancePage.jsx    # Records table + CSV export
│   │   │   ├── ReportsPage.jsx       # Deep analytics
│   │   │   └── ChatPage.jsx          # AI assistant interface
│   │   ├── components/layout/
│   │   │   └── Layout.jsx            # Sidebar navigation
│   │   ├── services/api.js           # Axios client (auto-attaches JWT)
│   │   └── store/
│   │       ├── authStore.js          # Zustand auth state
│   │       └── themeStore.js         # Dark/light toggle state
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── nginx.conf                    # Production Nginx config (Docker)
│   └── Dockerfile
│
├── ai-model/
│   ├── face_model.py             # Standalone CLI — register & match faces
│   └── emotion_model.py          # Standalone CLI + live webcam demo
│
├── storage/
│   ├── images/                   # Student reference photos
│   ├── embeddings/               # Face embedding JSON files
│   └── exports/                  # Generated CSV / Excel reports
│
├── docker-compose.yml
├── start.sh                      # One-command start (Linux/macOS)
├── start.bat                     # One-command start (Windows)
└── README.md
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Obtain JWT token |
| `/api/auth/me` | GET | Current authenticated user |
| `/api/students/` | GET / POST | List or create students |
| `/api/students/{id}` | GET / PUT / DELETE | Fetch, update, or remove a student |
| `/api/students/{id}/photo` | POST | Upload photo & register face embedding |
| `/api/attendance/` | GET | Paginated attendance records |
| `/api/attendance/stats` | GET | Today's attendance summary |
| `/api/analytics/overview` | GET | Dashboard overview data |
| `/api/analytics/alerts` | GET | Active alerts (low attendance, inactivity) |
| `/api/analytics/export/csv` | GET | Download attendance as CSV |
| `/api/analytics/export/xlsx` | GET | Download attendance as Excel |
| `/api/monitor/ws/{session_id}` | WS | Live AI analysis pipeline |
| `/api/chat/` | POST | Send a message to the AI chatbot |
| `/api/chat/health` | GET | Ollama connectivity status |
| `/health` | GET | API health check |

Full interactive docs (Swagger UI): **http://localhost:8000/docs**

---

## 🛠️ AI Model Details

### Face Recognition

- Uses **InsightFace `buffalo_sc`** — downloads automatically on first run (~100 MB).
- Falls back to **OpenCV Haar Cascades** if InsightFace is unavailable.
- Embeddings are stored as JSON files in `storage/embeddings/` and cached in memory at startup.
- Matching uses **cosine similarity** against the threshold set in `FACE_RECOGNITION_THRESHOLD`.

### Emotion Detection

- **DeepFace** classifies 7 emotions: `angry`, `disgust`, `fear`, `happy`, `sad`, `surprise`, `neutral`.
- Runs per-face within each processed frame (every `FRAME_SKIP` frames).

### Attention Tracking

- Head pose estimated with OpenCV `solvePnP` using facial landmark geometry.
- A student is considered "attentive" when both yaw and pitch fall within acceptable thresholds.
- Can be disabled via `ATTENTION_TRACKING_ENABLED=false` to reduce CPU load.

### Minimum Presence Time

Attendance is only marked after a student is **continuously detected for `MIN_PRESENCE_SECONDS`** (default 300 s / 5 minutes). The counter resets if the face disappears from the frame.

---

## 📡 WebSocket Protocol

Connect to `ws://<host>/api/monitor/ws/{session_id}` and send JPEG frames:

```json
{ "type": "frame", "data": "<base64-encoded JPEG>" }
```

Receive per-frame analysis:

```json
{
  "type": "analysis",
  "data": {
    "faces": [
      {
        "bbox": [x1, y1, x2, y2],
        "student_name": "Jane Doe",
        "recognition_confidence": 0.91,
        "emotion": "happy",
        "is_attentive": true
      }
    ],
    "activity": {
      "is_active": true,
      "motion_score": 0.004
    }
  }
}
```

---

## 📦 Standalone AI Tools

```bash
# Register a student face from an image file
python ai-model/face_model.py --mode register --image photo.jpg --student-id STU001

# Identify a person in an unknown image
python ai-model/face_model.py --mode match --image unknown.jpg

# Live emotion detection via webcam
python ai-model/emotion_model.py --mode realtime

# Analyse emotion in a single image
python ai-model/emotion_model.py --mode image --image face.jpg --show
```

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI 0.111 + Uvicorn |
| Database ORM | SQLAlchemy 2.0 (async) + aiosqlite |
| Database | SQLite (default) / PostgreSQL (optional) |
| Migrations | Alembic |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Rate limiting | SlowAPI |
| Face AI | InsightFace 0.7 + ONNX Runtime |
| Emotion AI | DeepFace 0.0.92 |
| Computer vision | OpenCV 4.9 (headless) |
| Export | openpyxl (Excel) + ReportLab (PDF) |
| Frontend | React 18 + Vite 5 |
| Styling | Tailwind CSS 3 + Radix UI |
| State management | Zustand |
| Charts | Recharts |
| Animations | Framer Motion |
| HTTP client | Axios |
| LLM | Ollama (Llama 3 / Mistral) |
| Containerisation | Docker + Docker Compose |

---

## 🔒 Security Notes

1. Set a strong, unique `SECRET_KEY` (≥ 32 characters) in `.env` before any deployment.
2. Change the default `admin` and `teacher` passwords on first login.
3. Terminate with `DEBUG=false` in production.
4. Use HTTPS — add TLS termination in the `nginx.conf` included with the frontend.
5. Consider switching from SQLite to PostgreSQL for any multi-user or high-load environment.
6. The API includes **rate limiting** via SlowAPI — review the limits in the route files and tighten them as appropriate.

---

## 🐛 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| InsightFace fails to load | First-run model download not complete | Wait for download, or check internet access |
| `onnxruntime` crash on Apple Silicon | CPU-only ONNX runtime | `pip install onnxruntime-silicon` |
| WebSocket drops frames | `FRAME_SKIP` too low for hardware | Increase `FRAME_SKIP` in `.env` |
| Chatbot returns "Ollama unavailable" | Ollama not running | Run `ollama serve` in a separate terminal |
| CORS errors in browser | Frontend origin not whitelisted | Add the origin to `ALLOWED_ORIGINS` in `.env` |
| Students not marked present | Below `MIN_PRESENCE_SECONDS` threshold | Reduce threshold or keep student in frame longer |
| Face not recognised | Threshold too strict, or poor reference photo | Lower `FACE_RECOGNITION_THRESHOLD` or re-upload photo in better lighting |

---

## 📄 License

MIT License — free for personal and commercial use.
