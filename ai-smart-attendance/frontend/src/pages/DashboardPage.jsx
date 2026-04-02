import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend
} from 'recharts'
import { Users, UserCheck, UserX, TrendingUp, Bell, Smile, Brain, AlertTriangle } from 'lucide-react'
import { analyticsApi } from '../services/api'
import useAuthStore from '../store/authStore'
import { format, parseISO } from 'date-fns'

const CARD_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.4 } }),
}

const EMOTION_COLORS = {
  happy: '#10b981', neutral: '#6b7280', sad: '#3b82f6',
  angry: '#ef4444', surprise: '#f59e0b', fear: '#8b5cf6', disgust: '#84cc16',
}

function StatCard({ icon: Icon, label, value, sub, color, delay }) {
  return (
    <motion.div custom={delay} variants={CARD_VARIANTS} initial="hidden" animate="visible"
                className="stat-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
          <p className="font-display text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{value ?? '—'}</p>
          {sub && <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
        </div>
        <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: color + '22' }}>
          <Icon size={22} style={{ color }} />
        </div>
      </div>
    </motion.div>
  )
}

function SkeletonCard() {
  return <div className="stat-card"><div className="skeleton h-20 w-full" /></div>
}

export default function DashboardPage() {
  const [overview, setOverview] = useState(null)
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuthStore()

  useEffect(() => {
    const load = async () => {
      try {
        const [ov, tr] = await Promise.all([
          analyticsApi.overview(),
          analyticsApi.dailyTrend(14),
        ])
        setOverview(ov.data)
        setTrend(tr.data.trend || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const trendFormatted = trend.map((d) => ({
    ...d,
    label: (() => { try { return format(parseISO(d.date), 'MMM d') } catch { return d.date } })(),
  }))

  const emotionData = overview?.emotion_distribution || []

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {user?.full_name?.split(' ')[0]} 👋
          </p>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs px-3 py-2 rounded-xl"
             style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
          <span className="live-dot" />
          Live Updates
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard icon={Users}     label="Total Students"  value={overview?.total_students}   color="#6C9EFF" delay={0} />
            <StatCard icon={UserCheck} label="Present Today"   value={overview?.today_present}    sub={`${overview?.attendance_rate_today?.toFixed(0)}% rate`} color="#10b981" delay={1} />
            <StatCard icon={UserX}     label="Absent Today"    value={overview?.today_absent}     color="#ef4444" delay={2} />
            <StatCard icon={Brain}     label="Attention Rate"  value={`${overview?.attention_rate?.toFixed(0)}%`} sub="Last 7 days" color="#BDB2FF" delay={3} />
          </>
        )}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Attendance trend */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card p-6 xl:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-display font-semibold text-base" style={{ color: 'var(--text-primary)' }}>
              Attendance Trend
            </h2>
            <span className="text-xs px-2 py-1 rounded-lg" style={{ background: 'var(--surface)', color: 'var(--text-muted)' }}>
              Last 14 days
            </span>
          </div>
          {loading ? (
            <div className="skeleton h-48 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trendFormatted} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                <defs>
                  <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6C9EFF" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#6C9EFF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--surface-solid)', border: '1px solid var(--border)', borderRadius: '0.75rem', fontSize: 12 }}
                  labelStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
                />
                <Area type="monotone" dataKey="present" stroke="#6C9EFF" strokeWidth={2.5}
                      fill="url(#grad1)" dot={{ r: 3, fill: '#6C9EFF' }} activeDot={{ r: 5 }} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </motion.div>

        {/* Emotion distribution */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card p-6">
          <h2 className="font-display font-semibold text-base mb-5" style={{ color: 'var(--text-primary)' }}>
            Emotion Snapshot
          </h2>
          {loading || !emotionData.length ? (
            <div className="flex flex-col items-center justify-center h-48 gap-3">
              <div className="skeleton h-32 w-32 rounded-full" />
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No emotion data yet</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={emotionData} dataKey="count" nameKey="emotion" cx="50%" cy="50%"
                     innerRadius={55} outerRadius={80} paddingAngle={3}>
                  {emotionData.map((entry, i) => (
                    <Cell key={i} fill={EMOTION_COLORS[entry.emotion] || '#94a3b8'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: 'var(--surface-solid)', border: '1px solid var(--border)', borderRadius: '0.75rem', fontSize: 12 }}
                />
                <Legend formatter={(v) => <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </motion.div>
      </div>

      {/* Alerts */}
      <AlertsPanel />
    </div>
  )
}

function AlertsPanel() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.alerts(true).then((r) => {
      setAlerts(r.data.alerts || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const markRead = async (id) => {
    await analyticsApi.markAlertRead(id)
    setAlerts((prev) => prev.filter((a) => a.id !== id))
  }

  const SEVERITY_STYLE = {
    critical: 'border-l-red-400 bg-red-50 dark:bg-red-900/20',
    warning:  'border-l-amber-400 bg-amber-50 dark:bg-amber-900/20',
    info:     'border-l-blue-400 bg-blue-50 dark:bg-blue-900/20',
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell size={16} style={{ color: 'var(--primary)' }} />
          <h2 className="font-display font-semibold text-base" style={{ color: 'var(--text-primary)' }}>
            Active Alerts
          </h2>
          {alerts.length > 0 && (
            <span className="w-5 h-5 text-[10px] font-bold rounded-full flex items-center justify-center text-white"
                  style={{ background: '#ef4444' }}>{alerts.length}</span>
          )}
        </div>
      </div>
      {loading ? (
        <div className="space-y-2">
          {Array(3).fill(0).map((_, i) => <div key={i} className="skeleton h-12 w-full" />)}
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-3xl mb-2">✅</div>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No active alerts</p>
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.slice(0, 6).map((alert) => (
            <motion.div key={alert.id} layout exit={{ opacity: 0, x: 20 }}
                        className={`flex items-start justify-between gap-3 p-3 rounded-xl border-l-4 ${SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.info}`}>
              <div className="flex items-start gap-2 min-w-0">
                <AlertTriangle size={14} className="mt-0.5 flex-shrink-0 text-amber-500" />
                <div>
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{alert.message}</p>
                  <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <button onClick={() => markRead(alert.id)}
                      className="text-xs flex-shrink-0 px-2 py-1 rounded-lg hover:opacity-80 transition-opacity"
                      style={{ background: 'var(--border)', color: 'var(--text-muted)' }}>
                Dismiss
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
