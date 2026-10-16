import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../../components/ui/Card'
import { twinApi } from '../../api/client'
import { TwinResponse } from '../../types'
import { MetricCard } from '../../components/twin/MetricCard'

export function Twin() {
  const [sseConnected, setSseConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  
  const { data: twinData, isLoading, error, refetch } = useQuery({
    queryKey: ['twin'],
    queryFn: () => twinApi.get(),
    refetchInterval: 5000, // Fallback polling
  })
  
  useEffect(() => {
    // Connect to SSE
    const es = new EventSource(twinApi.stream())
    eventSourceRef.current = es
    
    es.onopen = () => setSseConnected(true)
    es.onerror = () => setSseConnected(false)
    
    es.addEventListener('scan.created', () => refetch())
    es.addEventListener('metrics.updated', () => refetch())
    es.addEventListener('twin.tick', () => refetch())
    
    return () => {
      es.close()
      eventSourceRef.current = null
    }
  }, [refetch])
  
  if (isLoading && !twinData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Digital Twin</h1>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${sseConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
            <span className="text-sm text-gray-600">{sseConnected ? 'Live' : 'Polling'}</span>
          </div>
        </div>
        <div className="grid md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => (
            <Card key={i} className="p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
              <div className="h-8 bg-gray-200 rounded w-3/4" />
            </Card>
          ))}
        </div>
      </div>
    )
  }
  
  const twin = twinData?.data as TwinResponse
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Digital Twin</h1>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${sseConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-600">{sseConnected ? 'Live SSE' : 'Polling (5s)'}</span>
        </div>
      </div>
      
      {/* Metric Strip */}
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
      
      {/* Graph View */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Waste Flow Graph</h2>
        <div className="aspect-video bg-gray-50 rounded-lg flex items-center justify-center">
          {twin?.graph.nodes && twin.graph.nodes.length > 0 ? (
            <div className="text-center text-gray-500">
              <p className="mb-2">React Flow graph would render here</p>
              <p className="text-sm">{twin.graph.nodes.length} nodes, {twin.graph.edges.length} edges</p>
            </div>
          ) : (
            <p className="text-gray-500">Loading graph...</p>
          )}
        </div>
      </Card>
    </div>
  )
}