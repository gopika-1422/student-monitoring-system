import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { ClipboardList, Search, Download, Filter, CalendarDays } from 'lucide-react'
import { attendanceApi, analyticsApi } from '../services/api'
import { format } from 'date-fns'

const STATUS_STYLE = {
  present: 'badge-present',
  absent:  'badge-absent',
  late:    'badge-late',
}

function DurationBadge({ seconds }) {
  if (!seconds) return <span style={{ color: 'var(--text-muted)' }}>—</span>
  const m = Math.floor(seconds / 60)
  const h = Math.floor(m / 60)
  return <span>{h > 0 ? `${h}h ${m % 60}m` : `${m}m`}</span>
}

export default function AttendancePage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [search, setSearch] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [classFilter, setClassFilter] = useState('')
  const [classes, setClasses] = useState([])
  const [exporting, setExporting] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const params = {
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate }),
        ...(classFilter && { class_name: classFilter }),
        ...(search && { student_code: search }),
        limit: 100,
      }
      const [recRes, statRes] = await Promise.all([
        attendanceApi.list(params),
        attendanceApi.stats(classFilter || undefined),
      ])
      setRecords(recRes.data.records || [])
      setStats(statRes.data)
    } catch {
      toast.error('Failed to load attendance')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // Load classes
    import('../services/api').then(({ studentsApi }) => {
      studentsApi.classes().then(r => setClasses(r.data.classes || []))
    })
  }, [startDate, endDate, classFilter])

  const handleExport = async () => {
    setExporting(true)
    try {
      const res = await analyticsApi.exportCsv({
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate }),
        ...(classFilter && { class_name: classFilter }),
      })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `attendance_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('CSV exported')
    } catch {
      toast.error('Export failed')
    } finally {
      setExporting(false)
    }
  }

  const filtered = records.filter(r =>
    !search || r.student_code.includes(search) || r.student_name?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title">Attendance Records</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {records.length} records found
          </p>
        </div>
        <button onClick={handleExport} disabled={exporting} className="btn-secondary">
          <Download size={15} /> {exporting ? 'Exporting…' : 'Export CSV'}
        </button>
      </div>

      {/* Stats row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Students', val: stats.total_students, color: '#6C9EFF' },
            { label: 'Present Today', val: stats.today_present, color: '#10b981' },
            { label: 'Absent Today', val: stats.today_absent, color: '#ef4444' },
            { label: 'Attendance Rate', val: `${stats.attendance_rate?.toFixed(0) ?? 0}%`, color: '#BDB2FF' },
          ].map(({ label, val, color }) => (
            <motion.div key={label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        className="glass-card px-5 py-4">
              <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
              <p className="font-display text-2xl font-bold" style={{ color }}>{val}</p>
            </motion.div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-48">
          <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>
            Search
          </label>
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input className="input pl-9" placeholder="Student ID or name…" value={search}
                   onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>From</label>
          <input type="date" className="input" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>To</label>
          <input type="date" className="input" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Class</label>
          <select className="input" value={classFilter} onChange={e => setClassFilter(e.target.value)}>
            <option value="">All Classes</option>
            {classes.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <button onClick={loadData} className="btn-secondary h-[44px]">
          <Filter size={14} /> Apply
        </button>
      </div>

      {/* Table */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                  className="glass-card overflow-hidden">
        <div className="table-container border-0">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>ID</th>
                <th>Class</th>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Duration</th>
                <th>Confidence</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array(8).fill(0).map((_, i) => (
                  <tr key={i}>{Array(9).fill(0).map((_, j) => (
                    <td key={j}><div className="skeleton h-4 w-full" /></td>
                  ))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12">
                    <ClipboardList size={32} className="mx-auto mb-2 opacity-30" />
                    <p style={{ color: 'var(--text-muted)' }}>No records found</p>
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                             style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }}>
                          {(r.student_name || r.student_code)[0]}
                        </div>
                        <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                          {r.student_name || '—'}
                        </span>
                      </div>
                    </td>
                    <td><code className="text-xs font-mono px-2 py-0.5 rounded-lg" style={{ background: 'var(--border)' }}>{r.student_code}</code></td>
                    <td style={{ color: 'var(--text-secondary)' }}>{r.class_name}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      <span className="flex items-center gap-1">
                        <CalendarDays size={12} />
                        {r.date}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{r.check_in ? r.check_in.split('.')[0].split('T')[1] : '—'}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{r.check_out ? r.check_out.split('.')[0].split('T')[1] : '—'}</td>
                    <td><DurationBadge seconds={r.duration_seconds} /></td>
                    <td>
                      <div className="flex items-center gap-1">
                        <div className="h-1.5 rounded-full flex-1 max-w-16"
                             style={{ background: 'var(--border)' }}>
                          <div className="h-full rounded-full"
                               style={{ width: `${(r.confidence_score || 0) * 100}%`, background: '#6C9EFF' }} />
                        </div>
                        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                          {((r.confidence_score || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td><span className={`badge ${STATUS_STYLE[r.status] || ''}`}>{r.status}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
