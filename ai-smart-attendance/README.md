# 🎓 AI Smart Attendance & Classroom Monitoring System

A **production-ready, fully free/local** AI-powered attendance system with real-time face recognition, emotion detection, attention tracking, and an intelligent chatbot — all running **100% on your machine** with no paid APIs.

---

## ✨ Features

### 🤖 AI Capabilities
| Feature | Technology |
|---------|-----------|
| Face Recognition | InsightFace + cosine similarity |
| Emotion Detection | DeepFace (7 emotions) |
| Head Pose / Attention | OpenCV solvePnP |
| Activity Detection | Frame difference analysis |
| AI Chatbot | Ollama (Llama3 / Mistral) |

### 📊 Core Modules
- **Live Monitor** — WebSocket camera feed with real-time overlays
- **Smart Attendance** — Auto-mark after 5+ minute confirmed presence
- **Emotion Logging** — Per-student emotion timeline
- **Analytics Dashboard** — Charts, trends, top students
- **Alert System** — Low attendance, inactive students
- **Export** — CSV reports

### 🎨 UI
- Glassmorphism design language
- Dark / Light mode toggle
- Fully responsive (mobile + desktop)
- Smooth Framer Motion animations
- Loading skeletons

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (optional, for chatbot)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env as needed

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open http://localhost:5173

### 3. AI Chatbot (Optional)

```bash
# Install Ollama from https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model (in another terminal)
ollama pull llama3
# OR for lighter model:
# ollama pull mistral
```

---

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |

> ⚠️ **Change passwords in production!**

---

## 📂 Project Structure

```
ai-smart-attendance/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py          # JWT auth endpoints
│   │   │   ├── students.py      # Student CRUD + photo upload
│   │   │   ├── attendance.py    # Attendance records
│   │   │   ├── analytics.py     # Reports, alerts, export
│   │   │   ├── monitor.py       # WebSocket AI pipeline
│   │   │   └── chat.py          # Ollama chatbot
│   │   ├── core/
│   │   │   ├── config.py        # Settings (pydantic)
│   │   │   └── security.py      # JWT + bcrypt
│   │   ├── db/
│   │   │   └── database.py      # SQLAlchemy async engine
│   │   ├── models/              # ORM models
│   │   ├── services/
│   │   │   ├── face_service.py      # InsightFace recognition
│   │   │   ├── emotion_service.py   # DeepFace + head pose
│   │   │   ├── attendance_service.py # Presence tracking
│   │   │   └── chatbot_service.py   # Ollama integration
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx    # Charts + stats
│   │   │   ├── StudentsPage.jsx     # CRUD + photo upload
│   │   │   ├── LiveMonitorPage.jsx  # WebSocket camera
│   │   │   ├── AttendancePage.jsx   # Records + export
│   │   │   ├── ReportsPage.jsx      # Deep analytics
│   │   │   └── ChatPage.jsx         # AI assistant
│   │   ├── components/layout/
│   │   │   └── Layout.jsx           # Sidebar nav
│   │   ├── services/api.js          # Axios client
│   │   └── store/
│   │       ├── authStore.js         # Zustand auth
│   │       └── themeStore.js        # Dark/light toggle
│   └── tailwind.config.js
│
├── ai-model/
│   ├── face_model.py            # Standalone CLI tool
│   └── emotion_model.py         # Standalone + webcam demo
│
├── storage/
│   ├── images/                  # Student photos
│   └── embeddings/              # Face embedding JSONs
│
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Get JWT token |
| `/api/auth/me` | GET | Current user |
| `/api/students/` | GET/POST | List / create students |
| `/api/students/{id}/photo` | POST | Upload + register face |
| `/api/attendance/` | GET | Attendance records |
| `/api/attendance/stats` | GET | Today's stats |
| `/api/analytics/overview` | GET | Dashboard overview |
| `/api/analytics/export/csv` | GET | Download CSV |
| `/api/monitor/ws/{session_id}` | WS | Live AI pipeline |
| `/api/chat/` | POST | AI chatbot query |
| `/api/chat/health` | GET | Ollama status |

Full interactive docs: **http://localhost:8000/docs**

---

## ⚙️ Configuration (.env)

```env
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=sqlite+aiosqlite:///./attendance.db
FACE_RECOGNITION_THRESHOLD=0.6    # 0-1, higher = stricter
MIN_PRESENCE_SECONDS=300          # 5 minutes before marking
FRAME_SKIP=3                      # Process every Nth frame
EMOTION_DETECTION_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## 🛠️ AI Model Notes

### Face Recognition
- Uses **InsightFace buffalo_sc** model (downloads automatically on first run)
- Falls back to **OpenCV Haar Cascades** if InsightFace unavailable
- Embeddings stored as JSON files in `storage/embeddings/`

### Minimum Presence Time
By default, attendance is only marked after a student is **continuously detected for 5 minutes** (configurable via `MIN_PRESENCE_SECONDS`).

### WebSocket Protocol
Send frames to `ws://host/api/monitor/ws/{session_id}`:
```json
{ "type": "frame", "data": "<base64 JPEG>" }
```
Receive analysis:
```json
{
  "type": "analysis",
  "data": {
    "faces": [
      {
        "bbox": [x1, y1, x2, y2],
        "student_name": "John Doe",
        "recognition_confidence": 0.87,
        "emotion": "happy",
        "is_attentive": true
      }
    ],
    "activity": { "is_active": true, "motion_score": 0.003 }
  }
}
```

---

## 📦 Standalone AI Tools

```bash
# Register a student face
python ai-model/face_model.py --mode register --image photo.jpg --student-id STU001

# Identify a person
python ai-model/face_model.py --mode match --image unknown.jpg

# Live emotion detection (webcam)
python ai-model/emotion_model.py --mode realtime

# Analyze emotion in an image
python ai-model/emotion_model.py --mode image --image face.jpg --show
```

---

## 🔒 Security Notes

1. Change `SECRET_KEY` in `.env` before deployment
2. Change default passwords after first login
3. Use HTTPS in production (add SSL to nginx config)
4. Set `DEBUG=false` in production

---

## 📄 License

MIT License — Free for personal and commercial use.
