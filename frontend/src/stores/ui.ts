import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  role: string
  name: string
  demo?: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isDemo: boolean
  setTokens: (access: string, refresh: string, user: User) => void
  setAccessToken: (access: string) => void
  setDemoMode: (enabled: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isDemo: false,
      setTokens: (access, refresh, user) => set({ accessToken: access, refreshToken: refresh, user, isDemo: user.demo || false }),
      setAccessToken: (accessToken) => set({ accessToken }),
      setDemoMode: (enabled) => set({ isDemo: enabled }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null, isDemo: false }),
    }),
    { name: 'recircle-auth', partialize: (s) => ({ user: s.user, accessToken: s.accessToken, refreshToken: s.refreshToken, isDemo: s.isDemo }) }
  )
)