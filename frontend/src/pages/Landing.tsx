import { NavLink } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { useAuthStore } from '../../stores/ui'

export function Landing() {
  const { isDemo, setDemoMode } = useAuthStore()
  
  const handleDemoClick = () => {
    setDemoMode(true)
  }
  
  return (
    <div className="max-w-4xl mx-auto text-center py-12">
      {/* Hero */}
      <div className="mb-16">
        <div className="inline-flex items-center gap-2 bg-primary-50 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
          <span>🚀</span>
          <span>Code Clash 2.0 • Track 06</span>
        </div>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight mb-6">
          Smart Recycling Assistant
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Computer Vision × Digital Twin × Generative AI.
          Scan waste, see system impact, get grounded advice.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button size="lg" onClick={handleDemoClick} className="w-full sm:w-auto">
            <span className="mr-2">📷</span>
            Try Demo Scan
          </Button>
          <Button variant="secondary" size="lg" onClick={handleDemoClick} className="w-full sm:w-auto">
            View Digital Twin
          </Button>
        </div>
      </div>
      
      {/* Demo Notice */}
      {isDemo && (
        <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-lg" role="status">
          <p className="text-amber-800 font-medium">Demo mode active — using simulated campus data</p>
        </div>
      )}
      
      {/* Value Props */}
      <div className="grid md:grid-cols-3 gap-6 mb-16">
        <Card className="p-6">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-4 text-2xl">📷</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Instant Classification</h3>
          <p className="text-gray-600">Point camera at any waste item. Get recyclable, reusable, biodegradable, hazardous, or residual classification in under 3 seconds.</p>
        </Card>
        <Card className="p-6">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4 text-2xl">🔄</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Digital Twin</h3>
          <p className="text-gray-600">Every scan feeds a campus waste flow simulation. See diversion rates, contamination, CO2e avoided, and pickup costs update in real time.</p>
        </Card>
        <Card className="p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 text-2xl">🤖</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Grounded AI Advisor</h3>
          <p className="text-gray-600">Get personalized recommendations backed by twin metrics — never invented numbers. What-if scenarios test changes before spending.</p>
        </Card>
      </div>
      
      {/* How it Works */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="relative">
            <div className="absolute left-1/2 top-0 -translate-x-1/2 w-1 h-full bg-primary-200 hidden md:block" />
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl mb-4 relative z-10">1</div>
              <h3 className="font-semibold text-gray-900 mb-1">Scan</h3>
              <p className="text-gray-600 text-sm text-center">Take a photo or upload an image of waste</p>
            </div>
          </div>
          <div className="relative">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-2xl mb-4 relative z-10">2</div>
              <h3 className="font-semibold text-gray-900 mb-1">Analyze</h3>
              <p className="text-gray-600 text-sm text-center">CV classifies material, twin updates flow</p>
            </div>
          </div>
          <div className="relative">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center text-2xl mb-4 relative z-10">3</div>
              <h3 className="font-semibold text-gray-900 mb-1">Advise</h3>
              <p className="text-gray-600 text-sm text-center">AI recommends actions with quantified impact</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Tech Stack */}
      <div className="border-t border-gray-200 pt-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Built With</h2>
        <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-gray-600">
          <span className="px-3 py-1 bg-gray-100 rounded">React 18</span>
          <span className="px-3 py-1 bg-gray-100 rounded">TypeScript</span>
          <span className="px-3 py-1 bg-gray-100 rounded">Vite</span>
          <span className="px-3 py-1 bg-gray-100 rounded">Tailwind</span>
          <span className="px-3 py-1 bg-gray-100 rounded">FastAPI</span>
          <span className="px-3 py-1 bg-gray-100 rounded">PyTorch</span>
          <span className="px-3 py-1 bg-gray-100 rounded">MobileNetV3</span>
          <span className="px-3 py-1 bg-gray-100 rounded">React Flow</span>
          <span className="px-3 py-1 bg-gray-100 rounded">Recharts</span>
          <span className="px-3 py-1 bg-gray-100 rounded">SSE</span>
        </div>
      </div>
    </div>
  )
}