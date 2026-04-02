import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { Plus, Search, Upload, User, Trash2, Edit3, Camera, CheckCircle, XCircle, X } from 'lucide-react'
import { studentsApi } from '../services/api'

function StudentModal({ student, onClose, onSaved }) {
  const [form, setForm] = useState(student || {
    student_id: '', full_name: '', email: '', phone: '', class_name: 'CS-A', section: ''
  })
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      if (student) {
        await studentsApi.update(student.student_id, form)
        toast.success('Student updated')
      } else {
        await studentsApi.create(form)
        toast.success('Student created')
      }
      onSaved()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Error saving student')
    } finally {
      setSaving(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }}
                  className="glass-card w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display font-semibold text-lg gradient-text">
            {student ? 'Edit Student' : 'Add New Student'}
          </h2>
          <button onClick={onClose} style={{ color: 'var(--text-muted)' }} className="hover:opacity-70">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Full Name *</label>
            <input className="input" required value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} placeholder="John Doe" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Student ID *</label>
            <input className="input" required value={form.student_id} onChange={e => setForm({...form, student_id: e.target.value})} placeholder="STU001" disabled={!!student} />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Class</label>
            <input className="input" value={form.class_name} onChange={e => setForm({...form, class_name: e.target.value})} placeholder="CS-A" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Email</label>
            <input className="input" type="email" value={form.email || ''} onChange={e => setForm({...form, email: e.target.value})} placeholder="student@school.edu" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Phone</label>
            <input className="input" value={form.phone || ''} onChange={e => setForm({...form, phone: e.target.value})} placeholder="+1234567890" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: 'var(--text-secondary)' }}>Section</label>
            <input className="input" value={form.section || ''} onChange={e => setForm({...form, section: e.target.value})} placeholder="Morning" />
          </div>
          <div className="col-span-2 flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : (student ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  )
}

function PhotoUploadModal({ student, onClose }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef()

  const handleFile = (f) => {
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const res = await studentsApi.uploadPhoto(student.student_id, file)
      toast.success(res.data.message)
      onClose()
    } catch (err) {
      toast.error('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
                  className="glass-card w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display font-semibold text-lg gradient-text">Upload Face Photo</h2>
          <button onClick={onClose} style={{ color: 'var(--text-muted)' }}><X size={20} /></button>
        </div>
        <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
          For: <strong style={{ color: 'var(--text-primary)' }}>{student.full_name}</strong>
        </p>
        <div
          onClick={() => fileRef.current.click()}
          className="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors hover:border-blue-400"
          style={{ borderColor: 'var(--border)' }}
        >
          {preview ? (
            <img src={preview} alt="Preview" className="w-32 h-32 object-cover rounded-xl mx-auto" />
          ) : (
            <div className="text-center space-y-2">
              <Camera size={32} className="mx-auto" style={{ color: 'var(--text-muted)' }} />
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Click to select photo</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>JPG, PNG — clear frontal face</p>
            </div>
          )}
          <input ref={fileRef} type="file" accept="image/*" className="hidden"
                 onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])} />
        </div>
        <div className="flex gap-3 mt-4">
          <button onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
          <button onClick={handleUpload} disabled={!file || uploading} className="btn-primary flex-1 justify-center">
            {uploading ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : 'Upload & Register'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function StudentsPage() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | 'add' | 'edit' | 'photo'
  const [selected, setSelected] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await studentsApi.list({ search, limit: 100 })
      setStudents(res.data)
    } catch (e) {
      toast.error('Failed to load students')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search])

  const handleDelete = async (id) => {
    if (!confirm('Deactivate this student?')) return
    try {
      await studentsApi.delete(id)
      toast.success('Student deactivated')
      load()
    } catch { toast.error('Error') }
  }

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Students</h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {students.length} registered students
          </p>
        </div>
        <button onClick={() => { setSelected(null); setModal('add') }} className="btn-primary">
          <Plus size={16} /> Add Student
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input className="input pl-10" placeholder="Search by name or ID..." value={search}
               onChange={(e) => setSearch(e.target.value)} />
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
                <th>Email</th>
                <th>Face Data</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <tr key={i}>
                    {Array(6).fill(0).map((_, j) => (
                      <td key={j}><div className="skeleton h-5 w-full" /></td>
                    ))}
                  </tr>
                ))
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12">
                    <User size={32} className="mx-auto mb-2 opacity-30" />
                    <p style={{ color: 'var(--text-muted)' }}>No students found</p>
                  </td>
                </tr>
              ) : (
                students.map((s) => (
                  <motion.tr key={s.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} layout>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                             style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }}>
                          {s.full_name[0]}
                        </div>
                        <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{s.full_name}</span>
                      </div>
                    </td>
                    <td><code className="text-xs font-mono px-2 py-0.5 rounded-lg" style={{ background: 'var(--border)' }}>{s.student_id}</code></td>
                    <td><span className="badge" style={{ background: 'var(--border)', color: 'var(--text-secondary)' }}>{s.class_name}</span></td>
                    <td style={{ color: 'var(--text-muted)' }}>{s.email || '—'}</td>
                    <td>
                      {s.has_face_data
                        ? <span className="flex items-center gap-1 text-emerald-500 text-xs"><CheckCircle size={13} /> Registered</span>
                        : <span className="flex items-center gap-1 text-amber-500 text-xs"><XCircle size={13} /> Missing</span>
                      }
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <button onClick={() => { setSelected(s); setModal('photo') }}
                                title="Upload photo"
                                className="p-1.5 rounded-lg hover:opacity-80 transition-opacity"
                                style={{ color: 'var(--primary)' }}>
                          <Camera size={15} />
                        </button>
                        <button onClick={() => { setSelected(s); setModal('edit') }}
                                className="p-1.5 rounded-lg hover:opacity-80 transition-opacity"
                                style={{ color: 'var(--text-secondary)' }}>
                          <Edit3 size={15} />
                        </button>
                        <button onClick={() => handleDelete(s.student_id)}
                                className="p-1.5 rounded-lg hover:opacity-80 transition-opacity text-red-400">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      <AnimatePresence>
        {(modal === 'add' || modal === 'edit') && (
          <StudentModal student={modal === 'edit' ? selected : null}
                        onClose={() => setModal(null)} onSaved={() => { setModal(null); load() }} />
        )}
        {modal === 'photo' && selected && (
          <PhotoUploadModal student={selected} onClose={() => { setModal(null); load() }} />
        )}
      </AnimatePresence>
    </div>
  )
}
