export interface ScanResult {
  scan_id: string
  predicted_class: string
  subtype: string
  confidence: number
  top3: Array<{ class_name: string; confidence: number }>
  guidance: {
    bin: string
    steps: string[]
    why: string
    twin_effect: Record<string, any>
  }
  latency_ms: number
}

export interface ScanHistoryItem {
  id: number
  created_at: string
  predicted_class: string
  subtype: string
  confidence: number
  source_node_id?: number
  confirmed_bin?: string
  image_ref?: string
  latency_ms: number
}

export interface TwinNode {
  id: number
  type: string
  name: string
  config: Record<string, any>
  counts: Record<string, number>
  fill_level?: number
  contamination_rate?: number
  throughput?: number
}

export interface TwinEdge {
  id: number
  from_id: number
  to_id: number
  weight: number
  route_prob: number
}

export interface TwinGraph {
  nodes: TwinNode[]
  edges: TwinEdge[]
}

export interface Metrics {
  diversion_rate: number
  contamination_rate: number
  co2e_avoided_kg: number
  pickup_cost: number
  total_items: number
  recovered_items: number
  timestamp: string
}

export interface TwinResponse {
  graph: TwinGraph
  metrics: Metrics
}

export interface SimulateParams {
  compliance: number
  awareness_boost: number
  pickup_frequency: number
  bins_per_stream: number
  facility_yield_override?: Record<string, number>
  ticks: number
}

export interface ScenarioResult {
  params: Record<string, any>
  metrics: Metrics
}

export interface SimulateResponse {
  baseline: ScenarioResult
  scenario: ScenarioResult
  deltas: Record<string, number>
}

export interface AdviceAction {
  title: string
  why: string
  expected_impact: string
  effort: 'low' | 'medium' | 'high'
  owner: string
}

export interface AdviceResponse {
  summary: string
  issues: string[]
  actions: AdviceAction[]
  reuse_ideas: string[]
  disclaimer: string
  cached?: boolean
  provider?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface User {
  id: number
  email: string
  role: string
  name: string
  demo?: boolean
}