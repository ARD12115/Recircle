import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { CameraCapture } from '../../components/scan/CameraCapture'
import { ResultCard } from '../../components/scan/ResultCard'
import { UncertainState } from '../../components/scan/UncertainState'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { useScanSession } from '../../stores/scanSession'
import { scanApi } from '../../api/client'
import { ScanResult } from '../../types/scan'
import { api } from '../../api/client'

export function Scan() {
  const { image, previewUrl, result, loading, error, setImage, setPreviewUrl, setResult, setLoading, setError, clear } = useScanSession()
  const [confirmedBin, setConfirmedBin] = useState<string | null>(null)
  
  const scanMutation = useMutation({
    mutationFn: (file: File) => scanApi.scan(file),
    onMutate: () => {
      setLoading(true)
      setError(null)
    },
    onSuccess: (response) => {
      const data = response.data
      setResult(data)
      setConfirmedBin(null)
    },
    onError: (err: any) => {
      setError(err.message || 'Scan failed. Please try again.')
    },
    onSettled: () => setLoading(false),
  })
  
  const handleCapture = (file: File) => {
    scanMutation.mutate(file)
  }
  
  const handleConfirmBin = (bin: string) => {
    setConfirmedBin(bin)
    // In a real app, this would call a confirm endpoint
    console.log('Confirmed bin:', bin)
  }
  
  const handleRetake = () => {
    clear()
    setConfirmedBin(null)
  }
  
  const handleReport = () => {
    // Report incorrect classification
    console.log('Report:', result)
  }
  
  if (!image && !result) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Scan an Item</h1>
          <p className="text-gray-600 mt-2">Point your camera at a waste item to classify it</p>
        </div>
        <CameraCapture onCapture={handleCapture} />
      </div>
    )
  }
  
  if (result && result.predicted_class === 'unsure') {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Scan Result</h1>
        </div>
        <UncertainState result={result} onRetake={handleRetake} />
      </div>
    )
  }
  
  if (result) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Scan Result</h1>
            <p className="text-gray-600 text-sm">Tap the bin you actually used</p>
          </div>
          <Button variant="ghost" onClick={handleRetake} size="sm">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retake
          </Button>
        </div>
        
        {previewUrl && (
          <div className="mb-4 aspect-video bg-gray-100 rounded-xl overflow-hidden">
            <img src={previewUrl} alt="Scanned item" className="w-full h-full object-cover" />
          </div>
        )}
        
        <ResultCard
          result={result}
          onConfirmBin={handleConfirmBin}
          onRetake={handleRetake}
          onReport={handleReport}
        />
        
        {confirmedBin && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg" role="status">
            <div className="flex items-center gap-2 text-green-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-medium">Confirmed: {confirmedBin}</span>
            </div>
          </div>
        )}
      </div>
    )
  }
  
  return (
    <div className="max-w-2xl mx-auto">
      <CameraCapture onCapture={handleCapture} />
    </div>
  )
}