import { useQuery } from '@tanstack/react-query'
import { Card } from '../../components/ui/Card'
import { twinApi } from '../../api/client'
import { MetricCard } from '../../components/twin/MetricCard'

export function Facility() {
  const { data: twinData } = useQuery({
    queryKey: ['twin'],
    queryFn: () => twinApi.get(),
  })
  
  const twin = twinData?.data
  const bins = twin?.graph.nodes.filter(n => n.type === 'bin') || []
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Facility Dashboard</h1>
      
      {/* Summary Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Bins"
          value={bins.length}
          format="number"
          trend={0}
        />
        <MetricCard
          label="Avg Fill Level"
          value={bins.reduce((a, b) => a + (b.fill_level || 0), 0) / bins.length || 0}
          format="percent"
          trend={0}
        />
        <MetricCard
          label="Hotspots"
          value={bins.filter(b => (b.contamination_rate || 0) > 0.15).length}
          format="number"
          trend={0}
          negative={true}
        />
        <MetricCard
          label="Collection Due"
          value={bins.filter(b => (b.fill_level || 0) > 0.8).length}
          format="number"
          trend={0}
        />
      </div>
      
      {/* Bin Fill Levels */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Bin Fill Levels</h2>
        <div className="space-y-4">
          {bins.map(bin => (
            <div key={bin.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">{bin.name}</h3>
                <span className="text-sm font-mono text-gray-600">
                  {Math.round((bin.fill_level || 0) * 100)}%
                </span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    (bin.fill_level || 0) > 0.8 ? 'bg-red-500' :
                    (bin.fill_level || 0) > 0.5 ? 'bg-amber-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.round((bin.fill_level || 0) * 100)}%` }}
                />
              </div>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <span>Contamination: {Math.round((bin.contamination_rate || 0) * 100)}%</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  (bin.contamination_rate || 0) > 0.15 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                  {(bin.contamination_rate || 0) > 0.15 ? '⚠️ High' : 'OK'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Contamination Hotspots */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Contamination Hotspots</h2>
        <div className="space-y-3">
          {bins
            .filter(b => (b.contamination_rate || 0) > 0)
            .sort((a, b) => (b.contamination_rate || 0) - (a.contamination_rate || 0))
            .slice(0, 5)
            .map(bin => (
              <div key={bin.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{bin.name}</h3>
                    <p className="text-sm text-gray-500">
                      {Math.round((bin.contamination_rate || 0) * 100)}% contamination
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    (bin.contamination_rate || 0) > 0.2 ? 'bg-red-100 text-red-700' :
                    (bin.contamination_rate || 0) > 0.1 ? 'bg-amber-100 text-amber-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {(bin.contamination_rate || 0) > 0.2 ? 'Critical' :
                     (bin.contamination_rate || 0) > 0.1 ? 'High' : 'Moderate'}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </Card>
      
      {/* Export Report Button */}
      <Card className="p-6 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Export Sustainability Report</h3>
            <p className="text-sm text-gray-500">Generate a markdown report with metrics, issues, and recommendations</p>
          </div>
          <button className="btn-secondary">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Report
          </button>
        </div>
      </Card>
    </div>
  )
}