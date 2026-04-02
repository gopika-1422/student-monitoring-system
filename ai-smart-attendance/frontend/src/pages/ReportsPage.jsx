import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import { BarChart3, TrendingUp, AlertTriangle, Star, Download } from 'lucide-react'
import { attendanceApi, analyticsApi } from '../services/api'
import toast from 'react-hot-toast'

export default function ReportsPage() {
  const [topStudents, setTopStudents] = useState([])
  const [lowAlerts, setLowAlerts] = useState([])
  const [emotionTrend, setEmotionTrend] = useState([])
  const [dailyTrend, setDailyTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [top, low, emo, daily] = await Promise.all([
          attendanceApi.topStudents(10),
          attendanceApi.lowAttendance(75),
          analyticsApi.emotionTrend(7),
          analyticsApi.dailyTrend(days),
        ])
        setTopStudents(top.data.students || [])
        setLowAlerts(low.data.alerts || [])
        setEmotionTrend(emo.data.data || [])
        setDailyTrend(daily.data.trend || [])
      } catch { toast.error('Failed to load reports') }
      finally { setLoading(false) }
    }
    load()
  }, [days])

  const handleExport = async () => {
    setExporting(true)
    try {
      const res = await analyticsApi.exportCsv({})
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `full_report_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Report exported')
    } catch { toast.error('Export failed') }
    finally { setExporting(false) }
  }

  // Process emotion trend for chart
  const emotionChartData = (() => {
    const byDate = {}
    emotionTrend.forEach(({ date, emotion, count }) => {
      if (!byDate[date]) byDate[date] = { date }
      byDate[date][emotion] = count
    })
    return Object.values(byDate)
  })()

  const EMOTION_COLORS = ['#10b981','#6b7280','#3b82f6','#ef4444','#f59e0b','#8b5cf6','#84cc16']

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>Deep insights into attendance &amp; behavior</p>
        </div>
        <div className="flex items-center gap-3">
          <select value={days} onChange={e => setDays(Number(e.target.value))} className="input !py-2 w-36">
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button onClick={handleExport} disabled={exporting} className="btn-secondary">
            <Download size={15} /> {exporting ? 'Exporting…' : 'Export CSV'}
          </button>
        </div>
      </div>

      {/* Daily trend + emotion chart */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                    className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} style={{ color: 'var(--primary)' }} />
            <h2 className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>Daily Attendance</h2>
          </div>
          {loading ? <div className="skeleton h-52 w-full" /> : (
            <ResponsiveContainer width="100%" height={210}>
              <BarChart data={dailyTrend.slice(-14)} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6C9EFF" />
                    <stop offset="100%" stopColor="#BDB2FF" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} tickFormatter={v => v.slice(5)} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'var(--surface-solid)', border: '1px solid var(--border)', borderRadius: '0.75rem', fontSize: 12 }} />
                <Bar dataKey="present" fill="url(#barGrad)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                    className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={16} style={{ color: '#BDB2FF' }} />
            <h2 className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>Emotion Trends</h2>
          </div>
          {loading || emotionChartData.length === 0 ? (
            <div className="flex items-center justify-center h-52">
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                {loading ? 'Loading…' : 'No emotion data yet. Start monitoring to collect data.'}
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={210}>
              <LineChart data={emotionChartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'var(--surface-solid)', border: '1px solid var(--border)', borderRadius: '0.75rem', fontSize: 12 }} />
                <Legend formatter={v => <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{v}</span>} />
                {['happy','neutral','sad','angry','surprise'].map((e, i) => (
                  <Line key={e} type="monotone" dataKey={e} stroke={EMOTION_COLORS[i]} strokeWidth={2} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </motion.div>
      </div>

      {/* Top students + Low attendance */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Star size={16} style={{ color: '#FFD166' }} />
            <h2 className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>Top Attendees</h2>
          </div>
          {loading ? (
            <div className="space-y-2">{Array(5).fill(0).map((_, i) => <div key={i} className="skeleton h-10 w-full" />)}</div>
          ) : topStudents.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: 'var(--text-muted)' }}>No attendance data yet</p>
          ) : (
            <div className="space-y-2">
              {topStudents.map((s, i) => (
                <div key={s.student_code} className="flex items-center gap-3 p-3 rounded-xl"
                     style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                  <span className="w-6 text-center font-bold text-xs" style={{ color: i < 3 ? '#FFD166' : 'var(--text-muted)' }}>
                    {i < 3 ? ['🥇','🥈','🥉'][i] : `#${i+1}`}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{s.full_name || s.student_code}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <div className="h-1.5 flex-1 rounded-full" style={{ background: 'var(--border)' }}>
                        <div className="h-full rounded-full" style={{ width: `${Math.min(s.attendance_rate, 100)}%`, background: 'linear-gradient(90deg, #6C9EFF, #10b981)' }} />
                      </div>
                      <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>{s.attendance_rate}%</span>
                    </div>
                  </div>
                  <span className="text-xs font-semibold px-2 py-1 rounded-lg"
                        style={{ background: 'var(--border)', color: 'var(--text-secondary)' }}>
                    {s.present_count}d
                  </span>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                    className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={16} style={{ color: '#ef4444' }} />
            <h2 className="font-display font-semibold" style={{ color: 'var(--text-primary)' }}>Low Attendance Alerts</h2>
            {lowAlerts.length > 0 && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 font-semibold">
                {lowAlerts.length} at risk
              </span>
            )}
          </div>
          {loading ? (
            <div className="space-y-2">{Array(5).fill(0).map((_, i) => <div key={i} className="skeleton h-10 w-full" />)}</div>
          ) : lowAlerts.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-3xl mb-2">✅</div>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>All students above 75% threshold</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {lowAlerts.map((a) => (
                <div key={a.student_code} className="flex items-center gap-3 p-3 rounded-xl border-l-4 border-l-red-400"
                     style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderLeftWidth: '4px', borderLeftColor: '#ef4444' }}>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{a.full_name}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{a.student_code} · {a.present_days}/{a.total_days} days</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-red-500">{a.attendance_rate}%</p>
                    <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>attendance</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
