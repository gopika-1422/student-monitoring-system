import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username, password) => {
        const form = new FormData()
        form.append('username', username)
        form.append('password', password)
        const res = await api.post('/api/auth/login', form, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        const { access_token, user } = res.data
        set({ token: access_token, user, isAuthenticated: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        return user
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        delete api.defaults.headers.common['Authorization']
      },

      setToken: (token) => {
        set({ token })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },

      hydrate: () => {
        const token = get().token
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

export default useAuthStore
