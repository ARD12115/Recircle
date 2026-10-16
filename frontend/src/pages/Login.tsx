import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { authApi } from '../../api/client'
import { useAuthStore } from '../../stores/ui'

export function Login() {
  const navigate = useNavigate()
  const { setTokens, setDemoMode } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'login' | 'demo'>('login')
  
  const loginMutation = useMutation({
    mutationFn: () => authApi.login(email, password),
    onSuccess: (response) => {
      const { access_token, refresh_token, user } = response.data
      setTokens(access_token, refresh_token, user)
      navigate('/')
    },
    onError: (err: any) => {
      setError(err.response?.data?.message || 'Login failed')
    },
  })
  
  const demoMutation = useMutation({
    mutationFn: (role: string) => authApi.demo(role),
    onSuccess: (response) => {
      const { access_token, refresh_token, user } = response.data
      setTokens(access_token, refresh_token, user)
      setDemoMode(true)
      navigate('/')
    },
    onError: (err: any) => {
      setError(err.response?.data?.message || 'Demo login failed')
    },
  })
  
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    loginMutation.mutate()
  }
  
  const handleDemo = (role: string) => {
    setError('')
    demoMutation.mutate(role)
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mx-auto mb-4 text-3xl">
            ♻️
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome to ReCircle</h1>
          <p className="text-gray-600 mt-2">Sign in or try demo mode</p>
        </div>
        
        {/* Tab Switcher */}
        <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'login' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setActiveTab('demo')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'demo' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Demo Mode
          </button>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm" role="alert">
            {error}
          </div>
        )}
        
        {activeTab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="label">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="you@example.com"
                required
                disabled={loginMutation.isPending}
              />
            </div>
            <div>
              <label htmlFor="password" className="label">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
                required
                disabled={loginMutation.isPending}
              />
            </div>
            <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
              {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        )}
        
        {activeTab === 'demo' && (
          <div className="space-y-3">
            <p className="text-sm text-gray-500 text-center">
              Choose a role to try the demo
            </p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { role: 'resident', label: 'Resident', desc: 'Scan, history, impact' },
                { role: 'manager', label: 'Manager', desc: 'Twin, what-if, reports' },
                { role: 'admin', label: 'Admin', desc: 'Full access + demo controls' },
              ].map(({ role, label, desc }) => (
                <Button
                  key={role}
                  variant="secondary"
                  className="h-20 flex flex-col items-start gap-1 text-left"
                  onClick={() => handleDemo(role)}
                  disabled={demoMutation.isPending}
                >
                  <span className="font-medium">{label}</span>
                  <span className="text-xs text-gray-500">{desc}</span>
                </Button>
              ))}
            </div>
            <Button
              variant="secondary"
              className="w-full"
              onClick={() => handleDemo('guest')}
              disabled={demoMutation.isPending}
            >
              Guest (no account)
            </Button>
          </div>
        )}
        
        <div className="mt-6 pt-6 border-t border-gray-100 text-center text-sm text-gray-500">
          <p>Code Clash 2.0 • Track 06</p>
          <p>Computer Vision × Digital Twin × Generative AI</p>
        </div>
      </Card>
    </div>
  )
}