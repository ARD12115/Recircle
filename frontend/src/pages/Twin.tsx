import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../components/ui/Card'
import { twinApi } from '../api/client'
import { TwinResponse } from '../types'
import { MetricCard } from '../components/twin/MetricCard'
import ReactFlow, { Background, Controls, MiniMap } from 'react-flow-renderer'
import 'react-flow-renderer/dist/style.css'

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
  
  const twin = twinData?.data as TwinResponse | undefined
  const nodeRows = new Map<string, number>()
  const nodes = twin?.graph.nodes.map(node => {
    const row = nodeRows.get(node.type) ?? 0
    nodeRows.set(node.type, row + 1)
    const columns: Record<string, number> = { source: 0, bin: 1, collection: 2, facility: 3 }
    const count = Object.values(node.counts).reduce((sum, value) => sum + value, 0)
    return {
      id: String(node.id),
      position: { x: (columns[node.type] ?? 0) * 240, y: row * 105 },
      data: { label: `${node.name}${count ? ` · ${count} scanned` : ''}` },
      style: {
        borderRadius: 8,
        border: '1px solid #cbd5e1',
        background: node.type === 'source' ? '#eff6ff' : node.type === 'bin' ? '#f0fdf4' : '#f8fafc',
        padding: 10,
        width: 175,
      },
    }
  }) ?? []
  const edges = twin?.graph.edges.map(edge => ({
    id: String(edge.id),
    source: String(edge.from_id),
    target: String(edge.to_id),
    label: edge.weight > 0 ? String(edge.weight) : undefined,
    animated: edge.weight > 0,
    style: { strokeWidth: Math.min(5, 1 + edge.weight / 20) },
  })) ?? []
  
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
        />
        <MetricCard
          label="Contamination"
          value={twin?.metrics.contamination_rate}
          format="percent"
          negative={true}
        />
        <MetricCard
          label="CO₂e Avoided"
          value={twin?.metrics.co2e_avoided_kg}
          format="kg"
        />
        <MetricCard
          label="Pickup Cost"
          value={twin?.metrics.pickup_cost}
          format="currency"
          negative={true}
        />
      </div>
      
      {/* Graph View */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Waste Flow Graph</h2>
        <div className="twin-graph h-[600px]" aria-label="Campus waste flow graph">
          {error ? (
            <p className="p-6 text-red-600" role="alert">Twin data could not be loaded.</p>
          ) : twin?.graph.nodes.length ? (
            <ReactFlow nodes={nodes} edges={edges} fitView>
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          ) : twin ? (
            <p className="p-6 text-gray-500">No waste-flow nodes are available yet.</p>
          ) : (
            <p className="text-gray-500">Loading graph...</p>
          )}
        </div>
      </Card>
    </div>
  )
}