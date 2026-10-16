import { useQuery } from '@tanstack/react/query'
import { Card } from '../../components/ui/Card'
import { twinApi } from '../../api/client'
import { MetricCard } from '../../components/twin/MetricCard'
import { AdviceResponse } from '../../types'
import { adviceApi } from '../../api/client'

export function Impact() {
  const { data: twinData } = useQuery({
    queryKey: ['twin'],
    queryFn: () => twinApi.get(),
  })
  
  const { data: adviceData } = useQuery({
    queryKey: ['advice'],
    queryFn: () => adviceApi.get(true), // cached for demo
  })
  
  const twin = twinData?.data
  const advice = adviceData?.data as AdviceResponse
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Impact Dashboard</h1>
      
      {/* KPI Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <MetricCard
          label="Diversion Rate"
          value={twin?.metrics.diversion_rate}
          format="percent"
          trend={0}
        />
        <MetricCard
          label="Contamination"
          value={twin?.metrics.contamination_rate}
          format="percent"
          trend={0}
          negative={true}
        />
        <MetricCard
          label="CO₂e Avoided"
          value={twin?.metrics.co2e_avoided_kg}
          format="kg"
          trend={0}
        />
        <MetricCard
          label="Pickup Cost"
          value={twin?.metrics.pickup_cost}
          format="currency"
          trend={0}
          negative={true}
        />
      </div>
      
      {/* Trend Charts Placeholder */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Trends (Last 30 Days)</h2>
        <div className="aspect-video bg-gray-50 rounded-lg flex items-center justify-center">
          <p className="text-gray-500">Recharts line charts would render here</p>
        </div>
      </ Card>
      
      {/* Top Actions from Advisor */}
      {advice && advice.actions.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recommended Actions</h2>
          <div className="space-y-3">
            {advice.actions.slice(0, 3).map((action, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{action.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{action.why}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className={`px-2 py-0.5 text-xs rounded-full ${
                        action.effort === 'low' ? 'bg-green-100 text-green-700' :
                        action.effort === 'medium' ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {action.effort} effort
                      </span>
                      <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded-full">
                        {action.owner}
                      </span>
                    </div>
                  </div>
                  <span className="text-sm text-green-600 font-medium">{action.expected_impact}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}