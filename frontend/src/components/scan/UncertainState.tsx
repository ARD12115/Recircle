import { ScanResult } from '../../types'

interface UncertainStateProps {
  result: ScanResult
  onRetake: () => void
}

export function UncertainState({ result, onRetake }: UncertainStateProps) {
  const { top3 } = result
  const hazardousProb = top3.find(t => t.class_name === 'hazardous')?.confidence || 0
  const isHazardousPossible = hazardousProb > 0.2
  
  return (
    <div className="card overflow-hidden border-amber-200" role="alert">
      <div className="px-6 py-4 bg-amber-50 border-b border-amber-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-medium text-amber-900">Not sure what this is</h3>
            <p className="text-sm text-amber-700">The model couldn't confidently classify this item</p>
          </div>
        </div>
      </div>
      
      <div className="p-6 space-y-4">
        {isHazardousPossible && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <h4 className="font-medium text-red-900">⚠️ Hazardous material possible</h4>
                <p className="text-sm text-red-700 mt-1">
                  This item might contain hazardous materials (like batteries). 
                  <strong>Do not put it in a general bin.</strong> Hand it to facility staff for safe disposal.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {!isHazardousPossible && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Tips for better results</h4>
            <ul className="space-y-1 text-sm text-blue-700">
              <li>• Ensure good, even lighting</li>
              <li>• Center the item in the frame</li>
              <li>• Use a plain background if possible</li>
              <li>• Hold the camera steady</li>
              <li>• Try taking the photo from a different angle</li>
            </ul>
          </div>
        )}
        
        {top3.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Top guesses</h4>
            <div className="flex flex-wrap gap-2">
              {top3.map((item, i) => (
                <span key={i} className="badge bg-gray-100 text-gray-700">
                  {item.class_name} ({Math.round(item.confidence * 100)}%)
                </span>
              ))}
            </div>
          </div>
        )}
        
        <button
          onClick={onRetake}
          className="btn-primary w-full"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retake Photo
        </button>
      </div>
    </div>
  )
}