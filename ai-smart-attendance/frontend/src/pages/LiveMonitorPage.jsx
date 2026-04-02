import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import Webcam from 'react-webcam'
import {
  Video, VideoOff, Play, Square, RefreshCw, Users,
  Brain, Smile, Eye, Activity, Wifi, WifiOff, Settings
} from 'lucide-react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
const EMOTION_EMOJI = { happy: '😊', neutral: '😐', sad: '😢', angry: '😠', surprise: '😲', fear: '😨', disgust: '🤢' }
const EMOTION_COLOR = { happy: '#10b981', neutral: '#6b7280', sad: '#3b82f6', angry: '#ef4444', surprise: '#f59e0b', fear: '#8b5cf6', disgust: '#84cc16' }

function FaceBox({ face }) {
  const [x1, y1, x2, y2] = face.bbox || [0, 0, 0, 0]
  const isKnown = face.recognition_confidence > 0.6
  const color = isKnown ? '#10b981' : '#f59e0b'
  const emoColor = EMOTION_COLOR[face.emotion] || '#6b7280'

  return (
    <div style={{
      position: 'absolute',
      left: `${x1}px`, top: `${y1}px`,
      width: `${x2 - x1}px`, height: `${y2 - y1}px`,
      border: `2px solid ${color}`,
      borderRadius: '8px',
      boxShadow: `0 0 12px ${color}66`,
      pointerEvents: 'none',
    }}>
      {/* Name tag */}
      <div style={{
        position: 'absolute', bottom: '100%', left: 0, marginBottom: '4px',
        background: color, color: 'white', borderRadius: '6px',
        padding: '2px 8px', fontSize: '11px', fontWeight: 700,
        whiteSpace: 'nowrap', fontFamily: 'DM Sans, sans-serif',
      }}>
        {isKnown ? face.student_name : 'Unknown'}
        {isKnown && ` (${(face.recognition_confidence * 100).toFixed(0)}%)`}
      </div>
      {/* Emotion tag */}
      <div style={{
        position: 'absolute', top: '100%', left: 0, marginTop: '4px',
        background: emoColor + 'dd', color: 'white', borderRadius: '6px',
        padding: '2px 6px', fontSize: '10px', fontWeight: 600,
        whiteSpace: 'nowrap',
      }}>
        {EMOTION_EMOJI[face.emotion] || '😐'} {face.emotion}
        {!face.is_attentive && ' · 😴 Distracted'}
      </div>
    </div>
  )
}

export default function LiveMonitorPage() {
  const webcamRef = useRef(null)
  const wsRef = useRef(null)
  const intervalRef = useRef(null)
  const canvasRef = useRef(null)

  const [isStreaming, setIsStreaming] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [sessionId] = useState(() => crypto.randomUUID())
  const [fps, setFps] = useState(0)
  const [frameCount, setFrameCount] = useState(0)
  const [frameSkip, setFrameSkip] = useState(3)
  const [camError, setCamError] = useState(false)
  const [videoDims, setVideoDims] = useState({ w: 640, h: 480 })
  const fpsRef = useRef(0)
  const lastFpsTime = useRef(Date.now())

  // Connect WebSocket
  const connectWs = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    const ws = new WebSocket(`${WS_URL}/api/monitor/ws/${sessionId}`)
    ws.onopen = () => {
      setWsConnected(true)
      toast.success('Connected to AI monitor')
    }
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'analysis') {
        setAnalysis(msg.data)
        fpsRef.current++
        const now = Date.now()
        if (now - lastFpsTime.current >= 1000) {
          setFps(fpsRef.current)
          fpsRef.current = 0
          lastFpsTime.current = now
        }
      }
    }
    ws.onclose = () => { setWsConnected(false); setIsStreaming(false) }
    ws.onerror = () => { setWsConnected(false) }
    wsRef.current = ws
  }, [sessionId])

  const disconnectWs = useCallback(() => {
    clearInterval(intervalRef.current)
    wsRef.current?.close()
    setWsConnected(false)
    setIsStreaming(false)
    setAnalysis(null)
  }, [])

  // Start streaming frames
  const startStreaming = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      toast.error('Connect to AI monitor first')
      return
    }
    setIsStreaming(true)
    let tick = 0
    intervalRef.current = setInterval(() => {
      tick++
      if (tick % frameSkip !== 0) return
      const video = webcamRef.current?.video
      if (!video || video.readyState !== 4) return
      const canvas = canvasRef.current
      if (!canvas) return
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      const dataUrl = canvas.toDataURL('image/jpeg', 0.7)
      const base64 = dataUrl.split(',')[1]
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'frame', data: base64 }))
        setFrameCount((c) => c + 1)
      }
    }, 100)
  }

  const stopStreaming = () => {
    clearInterval(intervalRef.current)
    setIsStreaming(false)
  }

  useEffect(() => () => { clearInterval(intervalRef.current); wsRef.current?.close() }, [])

  const faces = analysis?.faces || []
  const presentCount = faces.filter(f => f.recognition_confidence > 0.6).length
  const attentiveCount = faces.filter(f => f.is_attentive).length

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Live Monitor</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Real-time face recognition &amp; emotion detection
          </p>
        </div>
        <div className="flex items-center gap-2">
          {wsConnected
            ? <span className="flex items-center gap-1.5 text-xs text-emerald-500 font-semibold"><span className="live-dot" /> AI Connected</span>
            : <span className="flex items-center gap-1.5 text-xs font-semibold" style={{ color: 'var(--text-muted)' }}><WifiOff size={12} /> Disconnected</span>
          }
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Camera feed */}
        <div className="xl:col-span-2 glass-card p-4 space-y-4">
          <div className="relative bg-black rounded-xl overflow-hidden" style={{ aspectRatio: '16/9', minHeight: 300 }}>
            {camError ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3"
                   style={{ background: 'var(--surface)' }}>
                <VideoOff size={40} style={{ color: 'var(--text-muted)' }} />
                <p style={{ color: 'var(--text-muted)' }}>Camera not available</p>
              </div>
            ) : (
              <Webcam
                ref={webcamRef}
                audio={false}
                className="absolute inset-0 w-full h-full object-cover"
                videoConstraints={{ width: 1280, height: 720, facingMode: 'user' }}
                onUserMediaError={() => setCamError(true)}
                onUserMedia={(stream) => {
                  const track = stream.getVideoTracks()[0]
                  const { width, height } = track.getSettings()
                  setVideoDims({ w: width || 640, h: height || 480 })
                }}
                style={{ borderRadius: '0.75rem' }}
              />
            )}

            {/* Face overlay boxes */}
            {analysis && !camError && (
              <div className="absolute inset-0" style={{ pointerEvents: 'none' }}>
                {faces.map((face, i) => <FaceBox key={i} face={face} />)}
              </div>
            )}

            {/* Live badge */}
            {isStreaming && (
              <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-red-500 text-white text-[11px] font-bold px-2.5 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                LIVE
              </div>
            )}

            {/* FPS */}
            {isStreaming && (
              <div className="absolute top-3 right-3 bg-black/60 text-white text-[11px] font-mono px-2 py-1 rounded-lg">
                {fps} fps · {frameCount} frames
              </div>
            )}
          </div>
          <canvas ref={canvasRef} className="hidden" />

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-3">
            {!wsConnected ? (
              <button onClick={connectWs} className="btn-primary">
                <Wifi size={15} /> Connect AI
              </button>
            ) : (
              <button onClick={disconnectWs} className="btn-secondary">
                <WifiOff size={15} /> Disconnect
              </button>
            )}

            {!isStreaming ? (
              <button onClick={startStreaming} disabled={!wsConnected || camError}
                      className="btn-primary disabled:opacity-50">
                <Play size={15} /> Start Monitoring
              </button>
            ) : (
              <button onClick={stopStreaming} className="btn-danger">
                <Square size={15} /> Stop
              </button>
            )}

            <button onClick={() => wsRef.current?.send(JSON.stringify({ type: 'reload_embeddings' }))}
                    disabled={!wsConnected} className="btn-secondary disabled:opacity-50">
              <RefreshCw size={15} /> Reload Faces
            </button>

            <div className="flex items-center gap-2 ml-auto">
              <Settings size={14} style={{ color: 'var(--text-muted)' }} />
              <label className="text-xs" style={{ color: 'var(--text-muted)' }}>Frame skip:</label>
              <select value={frameSkip} onChange={e => setFrameSkip(Number(e.target.value))}
                      className="input !py-1 !px-2 w-16 text-xs">
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
                <option value={5}>5</option>
              </select>
            </div>
          </div>
        </div>

        {/* Sidebar stats */}
        <div className="space-y-4">
          {/* Live stats */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="font-display font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
              Live Stats
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: Users, label: 'Detected', val: faces.length, color: '#6C9EFF' },
                { icon: Users, label: 'Recognized', val: presentCount, color: '#10b981' },
                { icon: Brain, label: 'Attentive', val: attentiveCount, color: '#BDB2FF' },
                { icon: Activity, label: 'Motion', val: analysis?.activity?.is_active ? 'Yes' : 'No', color: '#FFD166' },
              ].map(({ icon: Icon, label, val, color }) => (
                <div key={label} className="rounded-xl p-3 text-center"
                     style={{ background: color + '18', border: `1px solid ${color}33` }}>
                  <Icon size={18} className="mx-auto mb-1" style={{ color }} />
                  <p className="text-lg font-bold font-display" style={{ color }}>{val}</p>
                  <p className="text-[10px] font-medium" style={{ color: 'var(--text-muted)' }}>{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Detected faces list */}
          <div className="glass-card p-5">
            <h3 className="font-display font-semibold text-sm mb-3" style={{ color: 'var(--text-primary)' }}>
              Detected Faces ({faces.length})
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              <AnimatePresence>
                {faces.length === 0 ? (
                  <p className="text-xs text-center py-4" style={{ color: 'var(--text-muted)' }}>
                    {isStreaming ? 'No faces detected' : 'Start monitoring to detect faces'}
                  </p>
                ) : (
                  faces.map((face, i) => (
                    <motion.div key={i} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-3 p-2.5 rounded-xl"
                                style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                      <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                           style={{ background: face.recognition_confidence > 0.6 ? '#10b981' : '#f59e0b' }}>
                        {face.student_name?.[0] || '?'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
                          {face.recognition_confidence > 0.6 ? face.student_name : 'Unknown'}
                        </p>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                            {(face.recognition_confidence * 100).toFixed(0)}%
                          </span>
                          <span className="text-[10px]" style={{ color: EMOTION_COLOR[face.emotion] }}>
                            {EMOTION_EMOJI[face.emotion]} {face.emotion}
                          </span>
                        </div>
                      </div>
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${face.is_attentive ? 'bg-emerald-400' : 'bg-red-400'}`} />
                    </motion.div>
                  ))
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Session info */}
          <div className="glass-card p-4">
            <h3 className="font-display font-semibold text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
              SESSION INFO
            </h3>
            <div className="space-y-1.5 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
              <p>ID: <span style={{ color: 'var(--text-primary)' }}>{sessionId.slice(0, 16)}…</span></p>
              <p>Status: <span style={{ color: wsConnected ? '#10b981' : '#ef4444' }}>
                {wsConnected ? 'Connected' : 'Disconnected'}
              </span></p>
              <p>Frames: <span style={{ color: 'var(--text-primary)' }}>{frameCount}</span></p>
              <p>Min presence: <span style={{ color: 'var(--text-primary)' }}>5 min</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
