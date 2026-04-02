import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import {
  LayoutDashboard, Users, Video, ClipboardList,
  BarChart3, MessageSquare, LogOut, Menu, X,
  Moon, Sun, Cpu, Bell
} from 'lucide-react'
import useAuthStore from '../../store/authStore'
import useThemeStore from '../../store/themeStore'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/students',  icon: Users,           label: 'Students' },
  { to: '/monitor',   icon: Video,           label: 'Live Monitor' },
  { to: '/attendance',icon: ClipboardList,   label: 'Attendance' },
  { to: '/reports',   icon: BarChart3,       label: 'Reports' },
  { to: '/chat',      icon: MessageSquare,   label: 'AI Assistant' },
]

export default function Layout() {
  const { user, logout } = useAuthStore()
  const { isDark, toggle } = useThemeStore()
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-6 py-6 mb-2">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }}>
            <Cpu size={18} className="text-white" />
          </div>
          <div>
            <p className="font-display font-bold text-sm leading-tight gradient-text">SmartAttend</p>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>AI Classroom Monitor</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-1">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={18} />
            <span className="text-sm font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 pb-4 space-y-1">
        <button onClick={toggle} className="sidebar-item w-full">
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
          <span className="text-sm font-medium">{isDark ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <button onClick={handleLogout} className="sidebar-item w-full text-red-400 hover:text-red-500">
          <LogOut size={18} />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </div>

      {/* User */}
      <div className="mx-3 mb-4 p-3 rounded-xl glass-card">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
               style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))' }}>
            {user?.full_name?.[0] || 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
              {user?.full_name || 'User'}
            </p>
            <p className="text-[11px] capitalize" style={{ color: 'var(--text-muted)' }}>
              {user?.role || 'teacher'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-app">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-64 flex-col flex-shrink-0 border-r border-glass"
             style={{ background: 'var(--surface)', backdropFilter: 'blur(20px)' }}>
        <SidebarContent />
      </aside>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 z-40 lg:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 h-full w-64 z-50 lg:hidden border-r border-glass"
              style={{ background: 'var(--surface-solid)', backdropFilter: 'blur(20px)' }}
            >
              <button onClick={() => setMobileOpen(false)}
                      className="absolute top-4 right-4" style={{ color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar (mobile) */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-glass"
                style={{ background: 'var(--surface)', backdropFilter: 'blur(20px)' }}>
          <button onClick={() => setMobileOpen(true)} style={{ color: 'var(--text-primary)' }}>
            <Menu size={22} />
          </button>
          <span className="font-display font-bold gradient-text">SmartAttend</span>
          <button onClick={toggle} style={{ color: 'var(--text-muted)' }}>
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}
