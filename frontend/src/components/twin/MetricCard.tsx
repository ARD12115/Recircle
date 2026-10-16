interface MetricCardProps {
  label: string
  value: number | undefined
  format: 'percent' | 'kg' | 'currency' | 'number'
  trend?: number
  negative?: boolean
}

export function MetricCard({ label, value, format, trend, negative = false }: MetricCardProps) {
  const formatValue = (v: number | undefined) => {
    if (v === undefined) return '—'
    switch (format) {
      case 'percent':
        return `${(v * 100).toFixed(1)}%`
      case 'kg':
        return `${v.toFixed(1)} kg`
      case 'currency':
        return `$${v.toFixed(0)}`
      case 'number':
        return v.toLocaleString()
      default:
        return String(v)
    }
  }
  
  const trendColor = trend !== undefined && trend > 0 ? (negative ? 'text-red-600' : 'text-green-600') :
                     trend !== undefined && trend < 0 ? (negative ? 'text-green-600' : 'text-red-600') : 'text-gray-400'
  
  const trendIcon = trend !== undefined && trend > 0 ? (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
    </svg>
  ) : trend !== undefined && trend < 0 ? (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
  ) : (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
    </svg>
  )
  
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1 tabular-nums">{formatValue(value)}</p>
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 ${trendColor}`}>
            {trendIcon}
            <span className="text-sm font-medium tabular-nums">
              {trend > 0 ? '+' : ''}{trend.toFixed(1)}%
            </span>
          </div>
        )}
      </div>
    </div>
  )
}