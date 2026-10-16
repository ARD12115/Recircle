import { ReactNode } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/ui'
import { useScanSession } from '../../stores/scanSession'

const NAV_ITEMS = [
  { path: '/scan', label: 'Scan', icon: '📷', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/twin', label: 'Twin', icon: '🔄', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/simulate', label: 'What-If', icon: '📊', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/impact', label: 'Impact', icon: '🌍', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/advisor', label: 'Advisor', icon: '🤖', roles: ['resident', 'manager', 'admin'] },
  { path: '/history', label: 'History', icon: '📜', roles: ['resident', 'manager', 'admin'] },
  { path: '/facility', label: 'Facility', icon: '🏭', roles: ['manager', 'admin'] },
]

export function Layout() {
  const location = useLocation()
  const { user, isDemo, logout } = useAuthStore()
  const { clear } = useScanSession()
  
  const filteredNav = NAV_ITEMS.filter(item => 
    item.roles.includes(user?.role || 'guest')
  )
  
  const handleLogout = () => {
    logout()
    clear()
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <NavLink to="/" className="flex items-center gap-2 text-xl font-bold text-primary-600">
              <span className="text-2xl">♻️</span>
              <span>ReCircle</span>
            </NavLink>
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1" role="navigation" aria-label="Main navigation">
              {filteredNav.map(item => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => 
                    `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive 
                        ? 'bg-primary-50 text-primary-700' 
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`
                  }
                >
                  <span aria-hidden="true">{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
            
            {/* Right Side - User/Status */}
            <div className="flex items-center gap-4">
              {/* Demo Mode Banner */}
              {isDemo && (
                <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-800 rounded-full">
                  Demo Mode
                </span>
              )}
              
              {/* User Menu */}
              {user ? (
                <div className="flex items-center gap-3">
                  <span className="hidden sm:block text-sm text-gray-600">
                    {user.name} ({user.role})
                  </span>
                  <button onClick={handleLogout} className="btn-ghost text-sm">
                    Logout
                  </button>
                </div>
              ) : (
                <NavLink to="/login" className="btn-primary text-sm hidden sm:block">
                  Sign In
                </NavLink>
              )}
            </div>
          </div>
        </div>
        
        {/* Mobile Tab Bar */}
        <nav className="md:hidden border-t border-gray-200" role="navigation" aria-label="Mobile navigation">
          <div className="grid grid-cols-3 gap-1 p-2">
            {filteredNav.slice(0, 3).map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `flex flex-col items-center gap-1 px-2 py-2 rounded-lg text-xs transition-colors ${
                    isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600'
                  }`
                }
              >
                <span aria-hidden="true" className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
      </header>
      
      {/* Simulated Data Banner */}
      {(isDemo || location.pathname.startsWith('/twin') || location.pathname.startsWith('/simulate')) && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-1.5" role="status" aria-live="polite">
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-sm text-blue-800">
            <span aria-hidden="true">ℹ️</span>
            <span>Simulated campus data — not real measurements</span>
          </div>
        </div>
      )}
      
      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          ReCircle • Code Clash 2.0 Track 06 • Computer Vision × Digital Twin × Generative AI
        </div>
      </footer>
    </div>
  )
}