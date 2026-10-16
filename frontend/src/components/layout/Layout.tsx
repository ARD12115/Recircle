import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/ui'
import { useScanSession } from '../../stores/scanSession'

const NAV_ITEMS = [
  { path: '/scan', label: 'Scan', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/twin', label: 'Twin', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/simulate', label: 'What-If', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/impact', label: 'Impact', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/advisor', label: 'Advisor', roles: ['guest', 'resident', 'manager', 'admin'] },
  { path: '/history', label: 'History', roles: ['resident', 'manager', 'admin'] },
  { path: '/facility', label: 'Facility', roles: ['manager', 'admin'] },
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
      <header className="site-header sticky top-0">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between gap-4 h-18">
            <NavLink to="/" className="flex shrink-0 items-center gap-3 text-lg font-bold text-white">
              <span className="brand-mark" aria-hidden="true">♻︎</span>
              <span className="tracking-tight">ReCircle</span>
            </NavLink>

            <nav className="hidden md:flex min-w-0 items-center gap-1 overflow-x-auto scrollbar-hide" role="navigation" aria-label="Main navigation">
              {filteredNav.map(item => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => 
                    `nav-link rounded-full px-3 py-2 text-sm font-semibold transition-colors ${isActive ? 'nav-link-active' : ''}`
                  }
                >
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>

            <div className="flex shrink-0 items-center gap-3">
              {isDemo && (
                <span className="hidden sm:inline-flex rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-lime-200">Demo</span>
              )}

              {user ? (
                <div className="flex items-center gap-3">
                  <span className="hidden lg:block max-w-36 truncate text-sm text-white/75">
                    {user.name} <span className="text-lime-200">/ {user.role}</span>
                  </span>
                  <button onClick={handleLogout} className="rounded-full border border-white/30 px-3 py-2 text-sm font-semibold text-white transition hover:border-lime-200 hover:text-lime-200">
                    Log out
                  </button>
                </div>
              ) : (
                <NavLink to="/login" className="hidden rounded-full bg-lime-300 px-4 py-2 text-sm font-bold text-green-950 transition hover:bg-lime-200 sm:block">
                  Sign in
                </NavLink>
              )}
            </div>
          </div>
        </div>

        <nav className="md:hidden border-t border-white/15 px-3 py-2" role="navigation" aria-label="Mobile navigation">
          <div className="flex gap-2 overflow-x-auto scrollbar-hide">
            {filteredNav.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `nav-link min-w-fit rounded-full px-4 py-2 text-xs font-semibold transition-colors ${isActive ? 'nav-link-active' : ''}`
                }
              >
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
      </header>

      {(isDemo || location.pathname.startsWith('/twin') || location.pathname.startsWith('/simulate')) && (
        <div className="data-ribbon px-4 py-2" role="status" aria-live="polite">
          <div className="max-w-[1440px] mx-auto flex items-center justify-center gap-2 text-center text-xs font-bold uppercase tracking-[0.12em]">
            <span aria-hidden="true" className="text-base">i</span>
            <span>Simulated campus data. Not real measurements.</span>
          </div>
        </div>
      )}

      <main className="site-main flex-1 max-w-[1440px] mx-auto w-full px-4 py-8 sm:px-6 lg:py-10">
        <Outlet />
      </main>

      <footer className="site-footer mt-auto px-4 py-6">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-2 text-center text-xs sm:flex-row sm:items-center sm:justify-between sm:text-left">
          <span className="font-bold tracking-wide">ReCircle / campus circularity</span>
          <span className="text-white/70">Code Clash 2.0 | Track 06 | Computer Vision | Digital Twin | Generative AI</span>
        </div>
      </footer>
    </div>
  )
}