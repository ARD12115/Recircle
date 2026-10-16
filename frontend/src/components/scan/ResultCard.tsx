import { ScanResult } from '../../types'

interface ResultCardProps {
  result: ScanResult
  onConfirmBin: (bin: string) => void
  onRetake: () => void
  onReport: () => void
  confirmedBin: string | null
  confirming: boolean
}

const BIN_OPTIONS = [
  { id: 'recyclable', label: 'Recyclable Bin', color: 'blue' },
  { id: 'reusable', label: 'Reusable/Donation Bin', color: 'amber' },
  { id: 'biodegradable', label: 'Biodegradable/Compost Bin', color: 'green' },
  { id: 'hazardous', label: 'Hazardous Collection', color: 'red' },
  { id: 'residual', label: 'Residual/Landfill Bin', color: 'gray' },
]

export function ResultCard({ result, onConfirmBin, onRetake, onReport, confirmedBin, confirming }: ResultCardProps) {
  const { predicted_class, subtype, confidence, top3, guidance } = result
  
  const classLabels: Record<string, string> = {
    recyclable: 'Recyclable',
    reusable: 'Reusable',
    biodegradable: 'Biodegradable',
    hazardous: 'Hazardous',
    residual: 'Residual',
    unsure: 'Unsure',
  }
  
  const classColors: Record<string, string> = {
    recyclable: 'badge-recyclable',
    reusable: 'badge-reusable',
    biodegradable: 'badge-biodegradable',
    hazardous: 'badge-hazardous',
    residual: 'badge-residual',
    unsure: 'badge-unsure',
  }
  
  return (
    <div className="card overflow-hidden" role="region" aria-live="polite" aria-label="Scan result">
      {/* Class Badge */}
      <div className="px-6 py-4 bg-gradient-to-r from-primary-50 to-primary-100 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className={`${classColors[predicted_class]} text-lg px-4 py-1.5`}>
              {classLabels[predicted_class] || predicted_class}
            </span>
            {subtype && subtype !== 'unknown' && (
              <span className="text-sm text-gray-600 bg-white/80 px-3 py-1 rounded-full">
                {subtype}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-600 transition-all duration-500"
                style={{ width: `${confidence * 100}%` }}
                role="progressbar"
                aria-valuenow={Math.round(confidence * 100)}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
            <span className="text-sm font-mono text-gray-600 w-10 text-right">
              {Math.round(confidence * 100)}%
            </span>
          </div>
        </div>
      </div>
      
      <div className="p-6 space-y-6">
        {/* Top-3 Predictions */}
        {top3.length > 1 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Other possibilities</h4>
            <div className="flex flex-wrap gap-2">
              {top3.slice(1).map((item, i) => (
                <span key={i} className="badge bg-gray-100 text-gray-700">
                  {item.class_name} ({Math.round(item.confidence * 100)}%)
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Guidance */}
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
            <div className="flex items-center gap-2 text-sm font-medium text-blue-800 mb-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 4-5 4-5s4 3 4 5c0 1-.657 2.657-1.343 3.343z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Put in: {guidance.bin}</span>
            </div>
          </div>
          
          {guidance.steps.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Preparation steps</h4>
              <ul className="space-y-1">
                {guidance.steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                    <svg className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {step}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {guidance.why && (
            <p className="text-sm text-gray-500 bg-gray-50 p-3 rounded-lg">
              <span className="font-medium">Why: </span>{guidance.why}
            </p>
          )}
        </div>
        
        {/* Actions */}
        <div className="pt-4 border-t border-gray-100 space-y-3">
          <h4 className="text-sm font-medium text-gray-700">I put it in...</h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {BIN_OPTIONS.map(bin => (
              <button
                key={bin.id}
                onClick={() => onConfirmBin(bin.id)}
                disabled={Boolean(confirmedBin) || confirming}
                aria-pressed={confirmedBin === bin.id}
                className={`px-3 py-2 rounded-lg text-sm font-medium border-2 transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                  bin.color === 'blue' ? 'border-blue-300 text-blue-700 hover:bg-blue-50' :
                  bin.color === 'amber' ? 'border-amber-300 text-amber-700 hover:bg-amber-50' :
                  bin.color === 'green' ? 'border-green-300 text-green-700 hover:bg-green-50' :
                  bin.color === 'red' ? 'border-red-300 text-red-700 hover:bg-red-50' :
                  'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {bin.label}
              </button>
            ))}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={onRetake}
              className="btn-secondary flex-1"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retake
            </button>
            <button
              onClick={onReport}
              className="btn-ghost flex-1 text-red-600 hover:bg-red-50"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Not right?
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}