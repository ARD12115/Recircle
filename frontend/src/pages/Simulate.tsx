import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { twinApi } from '../api/client'
import { SimulateParams, SimulateResponse } from '../types'
import { MetricCard } from '../components/twin/MetricCard'
import { useScenarioStore } from '../stores/scenario'

export function Simulate() {
  const { 
    compliance, awarenessBoost, pickupFrequency, binsPerStream, facilityYieldOverride,
    setCompliance, setAwarenessBoost, setPickupFrequency, setBinsPerStream, reset
  } = useScenarioStore()
  
  const [simulateResult, setSimulateResult] = useState<SimulateResponse | null>(null)
  const [running, setRunning] = useState(false)
  
  const simulateMutation = useMutation({
    mutationFn: (params: SimulateParams) => twinApi.simulate(params),
    onMutate: () => setRunning(true),
    onSuccess: (response) => {
      setSimulateResult(response.data)
      setRunning(false)
    },
    onError: () => setRunning(false),
  })
  
  const handleRun = () => {
    simulateMutation.mutate({
      compliance,
      awareness_boost: awarenessBoost,
      pickup_frequency: pickupFrequency,
      bins_per_stream: binsPerStream,
      facility_yield_override: facilityYieldOverride,
      ticks: 30,
    })
  }
  
  const handleReset = () => {
    reset()
    setSimulateResult(null)
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">What-If Simulator</h1>
        <Button variant="secondary" onClick={handleReset} disabled={running}>
          Reset to Baseline
        </Button>
      </div>
      
      {/* Sliders */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Parameters</h2>
        <div className="space-y-6">
          <div>
            <label className="label">Compliance Rate: {Math.round(compliance * 100)}%</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={compliance}
              onChange={(e) => setCompliance(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <p className="text-sm text-gray-500 mt-1">Probability residents put items in correct bins</p>
          </div>
          
          <div>
            <label className="label">Awareness Boost: {Math.round(awarenessBoost * 100)}%</label>
            <input
              type="range"
              min="0"
              max="0.3"
              step="0.05"
              value={awarenessBoost}
              onChange={(e) => setAwarenessBoost(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <p className="text-sm text-gray-500 mt-1">Additional compliance from education campaigns</p>
          </div>
          
          <div>
            <label className="label">Pickup Frequency: {pickupFrequency.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={pickupFrequency}
              onChange={(e) => setPickupFrequency(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <p className="text-sm text-gray-500 mt-1">Collection schedule multiplier (1x = baseline)</p>
          </div>
          
          <div>
            <label className="label">Bins per Stream: {binsPerStream}</label>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={binsPerStream}
              onChange={(e) => setBinsPerStream(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <p className="text-sm text-gray-500 mt-1">Number of bins for each waste stream</p>
          </div>
        </div>
        
        <div className="mt-6 flex gap-4">
          <Button onClick={handleRun} disabled={running} className="flex-1">
            {running ? 'Running...' : 'Run Simulation'}
          </Button>
        </div>
      </Card>
      
      {/* Results */}
      {simulateResult && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-900">Results: Baseline vs Scenario</h2>
          
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-6 border-l-4 border-blue-500">
              <h3 className="font-semibold text-blue-900 mb-4">Baseline</h3>
              <div className="space-y-3">
                <MetricCard label="Diversion Rate" value={simulateResult.baseline.metrics.diversion_rate} format="percent" trend={0} />
                <MetricCard label="Contamination" value={simulateResult.baseline.metrics.contamination_rate} format="percent" trend={0} negative />
                <MetricCard label="CO₂e Avoided" value={simulateResult.baseline.metrics.co2e_avoided_kg} format="kg" trend={0} />
                <MetricCard label="Pickup Cost" value={simulateResult.baseline.metrics.pickup_cost} format="currency" trend={0} negative />
              </div>
            </Card>
            
            <Card className="p-6 border-l-4 border-green-500">
              <h3 className="font-semibold text-green-900 mb-4">Scenario</h3>
              <div className="space-y-3">
                <MetricCard 
                  label="Diversion Rate" 
                  value={simulateResult.scenario.metrics.diversion_rate} 
                  format="percent" 
                  trend={simulateResult.deltas.diversion_rate * 100} 
                />
                <MetricCard 
                  label="Contamination" 
                  value={simulateResult.scenario.metrics.contamination_rate} 
                  format="percent" 
                  trend={simulateResult.deltas.contamination_rate * 100} 
                  negative 
                />
                <MetricCard 
                  label="CO₂e Avoided" 
                  value={simulateResult.scenario.metrics.co2e_avoided_kg} 
                  format="kg" 
                  trend={simulateResult.deltas.co2e_avoided_kg} 
                />
                <MetricCard 
                  label="Pickup Cost" 
                  value={simulateResult.scenario.metrics.pickup_cost} 
                  format="currency" 
                  trend={simulateResult.deltas.pickup_cost} 
                  negative 
                />
              </div>
            </Card>
          </div>
          
          {/* Delta Summary */}
          <Card className="p-6 bg-gray-50">
            <h3 className="font-semibold text-gray-900 mb-4">Impact Summary</h3>
            <div className="grid md:grid-cols-4 gap-4 text-center">
              <div className={simulateResult.deltas.diversion_rate > 0 ? 'text-green-600' : 'text-red-600'}>
                <p className="text-2xl font-bold">{simulateResult.deltas.diversion_rate > 0 ? '+' : ''}{(simulateResult.deltas.diversion_rate * 100).toFixed(1)}%</p>
                <p className="text-sm text-gray-600">Diversion Change</p>
              </div>
              <div className={simulateResult.deltas.contamination_rate < 0 ? 'text-green-600' : 'text-red-600'}>
                <p className="text-2xl font-bold">{simulateResult.deltas.contamination_rate < 0 ? '' : '+'}{(simulateResult.deltas.contamination_rate * 100).toFixed(1)}%</p>
                <p className="text-sm text-gray-600">Contamination Change</p>
              </div>
              <div className={simulateResult.deltas.co2e_avoided_kg > 0 ? 'text-green-600' : 'text-red-600'}>
                <p className="text-2xl font-bold">{simulateResult.deltas.co2e_avoided_kg > 0 ? '+' : ''}{simulateResult.deltas.co2e_avoided_kg.toFixed(1)} kg</p>
                <p className="text-sm text-gray-600">CO₂e Change</p>
              </div>
              <div className={simulateResult.deltas.pickup_cost < 0 ? 'text-green-600' : 'text-red-600'}>
                <p className="text-2xl font-bold">{simulateResult.deltas.pickup_cost < 0 ? '' : '+'}${simulateResult.deltas.pickup_cost.toFixed(0)}</p>
                <p className="text-sm text-gray-600">Cost Change</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}