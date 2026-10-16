import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Landing } from './pages/Landing'
import { Scan } from './pages/Scan'
import { Twin } from './pages/Twin'
import { Simulate } from './pages/Simulate'
import { Impact } from './pages/Impact'
import { Advisor } from './pages/Advisor'
import { History } from './pages/History'
import { Facility } from './pages/Facility'
import { Login } from './pages/Login'
import { useAuthStore } from './stores/ui'

function PrivateRoute({ children, requiredRole }: { children: React.ReactNode; requiredRole?: string }) {
  const { user, isDemo } = useAuthStore()
  
  if (!user && !isDemo) {
    return <Navigate to="/login" replace />
  }
  
  if (requiredRole && user?.role) {
    const roles = ['guest', 'resident', 'manager', 'admin']
    const userRoleIndex = roles.indexOf(user.role)
    const requiredRoleIndex = roles.indexOf(requiredRole)
    if (userRoleIndex < requiredRoleIndex) {
      return <Navigate to="/" replace />
    }
  }
  
  return <>{children}</>
}

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="scan" element={<PrivateRoute><Scan /></PrivateRoute>} />
        <Route path="twin" element={<PrivateRoute><Twin /></PrivateRoute>} />
        <Route path="simulate" element={<PrivateRoute><Simulate /></PrivateRoute>} />
        <Route path="impact" element={<PrivateRoute><Impact /></PrivateRoute>} />
        <Route path="advisor" element={<PrivateRoute requiredRole="guest"><Advisor /></PrivateRoute>} />
        <Route path="history" element={<PrivateRoute requiredRole="resident"><History /></PrivateRoute>} />
        <Route path="facility" element={<PrivateRoute requiredRole="manager"><Facility /></PrivateRoute>} />
        <Route path="login" element={<Login />} />
      </Route>
    </Routes>
  )
}