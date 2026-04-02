import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { Send, Bot, User, Wifi, WifiOff, Sparkles, Trash2 } from 'lucide-react'
import { chatApi } from '../services/api'

const SUGGESTIONS = [
  'Show today\'s attendance summary',
  'Which students are absent today?',
  'Who has the lowest attendance this month?',
  'What is the average attendance rate?',
  'List recent alerts',
  'Which class has the best attendance?',
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 ${
        isUser
          ? 'text-white'
          : 'border border-glass'
      }`}
      style={isUser
        ? { background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }
        : { background: 'var(--surface)' }
      }>
        {isUser ? <User size={14} /> : <Bot size={14} style={{ color: 'var(--primary)' }} />}
      </div>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        <div
          className="px-4 py-3 rounded-2xl text-sm leading-relaxed"
          style={isUser ? {
            background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))',
            color: 'white',
            borderBottomRightRadius: '4px',
          } : {
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            color: 'var(--text-primary)',
            borderBottomLeftRadius: '4px',
            whiteSpace: 'pre-wrap',
          }}
        >
          {msg.content}
        </div>
        <span className="text-[10px] px-1" style={{ color: 'var(--text-muted)' }}>
          {msg.time}
        </span>
      </div>
    </motion.div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-xl flex items-center justify-center border border-glass"
           style={{ background: 'var(--surface)' }}>
        <Bot size={14} style={{ color: 'var(--primary)' }} />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-bl-[4px]"
           style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
        <div className="flex gap-1.5 items-center h-4">
          {[0, 1, 2].map(i => (
            <div key={i} className="w-1.5 h-1.5 rounded-full"
                 style={{
                   background: 'var(--primary)',
                   animation: `bounce 1.2s ease-in-out ${i * 0.15}s infinite`,
                 }} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hello! I\'m your AI attendance assistant powered by a local LLM.\n\nI can help you with:\n• Attendance summaries and reports\n• Student activity insights\n• Alert monitoring\n• Trend analysis\n\nAsk me anything about your classroom data!',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [ollamaStatus, setOllamaStatus] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    chatApi.health().then(r => setOllamaStatus(r.data)).catch(() => setOllamaStatus({ status: 'offline' }))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const content = text || input.trim()
    if (!content || loading) return

    const userMsg = {
      role: 'user',
      content,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    const history = messages.slice(-10).map(m => ({ role: m.role, content: m.content }))

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await chatApi.send(content, history)
      const assistantMsg = {
        role: 'assistant',
        content: res.data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errMsg = {
        role: 'assistant',
        content: '⚠️ Error connecting to AI assistant. Make sure Ollama is running:\n```\nollama serve\nollama pull llama3\n```',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">AI Assistant</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Powered by Ollama · Local LLM
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl ${
            ollamaStatus?.status === 'online'
              ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20'
              : 'text-red-500 bg-red-50 dark:bg-red-900/20'
          }`}>
            {ollamaStatus?.status === 'online' ? <Wifi size={12} /> : <WifiOff size={12} />}
            Ollama {ollamaStatus?.status || '…'}
          </div>
          <button
            onClick={() => setMessages(prev => [prev[0]])}
            className="btn-secondary !py-1.5 !px-3 text-xs"
          >
            <Trash2 size={12} /> Clear
          </button>
        </div>
      </div>

      {/* Ollama offline warning */}
      {ollamaStatus?.status === 'offline' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="p-3 rounded-xl border-l-4 border-l-amber-400 text-sm"
                    style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderLeftWidth: '4px', borderLeftColor: '#f59e0b' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Ollama not running.</strong>
          <span style={{ color: 'var(--text-muted)' }}> Start it: <code className="font-mono text-xs">ollama serve</code> then <code className="font-mono text-xs">ollama pull llama3</code></span>
        </motion.div>
      )}

      {/* Chat window */}
      <div className="flex-1 glass-card p-4 overflow-y-auto space-y-4 min-h-0">
        <AnimatePresence>
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && <TypingIndicator />}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map(s => (
            <button key={s} onClick={() => sendMessage(s)}
                    className="text-xs px-3 py-1.5 rounded-xl transition-all hover:opacity-80"
                    style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="glass-card p-3 flex items-end gap-3">
        <div className="flex-1">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about attendance, students, trends… (Enter to send)"
            rows={1}
            className="w-full resize-none outline-none text-sm bg-transparent"
            style={{
              color: 'var(--text-primary)',
              maxHeight: '120px',
              lineHeight: '1.5',
            }}
            onInput={(e) => {
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
            }}
          />
        </div>
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 text-white disabled:opacity-40 transition-opacity"
          style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }}
        >
          {loading
            ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            : <Send size={16} />
          }
        </motion.button>
      </div>

      {/* Bounce animation */}
      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  )
}
