import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CameraCapture } from '../components/scan/CameraCapture'
import { ResultCard } from '../components/scan/ResultCard'
import { UncertainState } from '../components/scan/UncertainState'
import { Button } from '../components/ui/Button'
import { useScanSession } from '../stores/scanSession'
import { scanApi, twinApi } from '../api/client'

export function Scan() {
  const { image, previewUrl, result, loading, error, setResult, setLoading, setError, clear } = useScanSession()
  const [confirmedBin, setConfirmedBin] = useState<string | null>(null)
  const [sourceNodeId, setSourceNodeId] = useState<number | null>(null)
  const [confirmationError, setConfirmationError] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const { data: twinResponse, isLoading: loadingTwin, error: twinError } = useQuery({
    queryKey: ['twin'],
    queryFn: () => twinApi.get(),
  })
  const sources = twinResponse?.data.graph.nodes.filter(node => node.type === 'source') ?? []
  
  const scanMutation = useMutation({
    mutationFn: (file: File) => scanApi.scan(file, sourceNodeId ?? undefined),
    onMutate: () => {
      setLoading(true)
      setError(null)
    },
    onSuccess: (response) => {
      const data = response.data
      setResult(data)
      setConfirmedBin(null)
    },
    onError: (err: Error) => {
      setError(err.message || 'Scan failed. Please try again.')
    },
    onSettled: () => setLoading(false),
  })

  const confirmMutation = useMutation({
    mutationFn: (bin: string) => scanApi.confirm(result!.scan_id, bin),
    onSuccess: (response) => {
      setConfirmedBin(response.data.confirmed_bin)
      setConfirmationError(null)
      queryClient.invalidateQueries({ queryKey: ['twin'] })
      queryClient.invalidateQueries({ queryKey: ['advice'] })
    },
    onError: (err: Error) => setConfirmationError(err.message || 'Could not save your bin choice. Please try again.'),
  })
  
  const handleCapture = (file: File) => {
    scanMutation.mutate(file)
  }
  
  const handleConfirmBin = (bin: string) => {
    setConfirmationError(null)
    confirmMutation.mutate(bin)
  }
  
  const handleRetake = () => {
    clear()
    setConfirmedBin(null)
    setConfirmationError(null)
  }
  
  const handleReport = () => {
    // Report incorrect classification
    console.log('Report:', result)
  }
  
  if (!result) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Scan an Item</h1>
          <p className="text-gray-600 mt-2">Choose where the item came from, then point your camera at it</p>
        </div>
        {loadingTwin ? (
          <p className="text-gray-600" role="status">Loading campus locations…</p>
        ) : twinError ? (
          <p className="text-red-600" role="alert">Campus locations could not be loaded. Refresh the page to try again.</p>
        ) : sources.length === 0 ? (
          <p className="text-amber-700" role="alert">No campus source locations are available for scanning.</p>
        ) : (
          <>
            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="scan-source">
              Item source
            </label>
            <select
              id="scan-source"
              value={sourceNodeId ?? ''}
              onChange={event => setSourceNodeId(event.target.value ? Number(event.target.value) : null)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 mb-4"
            >
              <option value="">Choose a campus location</option>
              {sources.map(source => <option key={source.id} value={source.id}>{source.name}</option>)}
            </select>
            {image && loading ? (
              <p className="text-gray-600" role="status">Classifying item…</p>
            ) : sourceNodeId ? (
              <CameraCapture onCapture={handleCapture} />
            ) : (
              <p className="text-sm text-gray-600" role="status">Select a campus location to start a scan.</p>
            )}
          </>
        )}
        {error && <p className="mt-4 text-red-600" role="alert">{error}</p>}
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
          confirmedBin={confirmedBin}
          confirming={confirmMutation.isPending}
        />
        {confirmationError && <p className="mt-4 text-red-600" role="alert">{confirmationError}</p>}
        
        {confirmedBin && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg" role="status">
            <div className="flex items-center gap-2 text-green-800">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-medium">Confirmed: {confirmedBin.replace(/_/g, ' ')}</span>
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