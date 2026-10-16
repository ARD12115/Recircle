import { ChangeEvent, useRef, useState } from 'react'
import { useScanSession } from '../../stores/scanSession'
import { processImageFile } from '../../lib/image'

export function CameraCapture({ onCapture }: { onCapture: (file: File) => void }) {
  const { setImage, setPreviewUrl, setError, loading } = useScanSession()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment')
  const [permissionDenied, setPermissionDenied] = useState(false)
  
  const startCamera = async () => {
    try {
      setPermissionDenied(false)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      console.error('Camera access denied:', err)
      setPermissionDenied(true)
      setError('Camera permission denied. Please use file upload.')
    }
  }
  
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }
  
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return
    
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0)
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
          setImage(file)
          const url = URL.createObjectURL(file)
          setPreviewUrl(url)
          onCapture(file)
        }
      }, 'image/jpeg', 0.85)
    }
  }
  
  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const processed = processImageFile(file)
      setImage(processed)
      const url = URL.createObjectURL(processed)
      setPreviewUrl(url)
      onCapture(processed)
    }
  }
  
  const switchCamera = () => {
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment')
    stopCamera()
    startCamera()
  }
  
  return (
    <div className="space-y-4">
      {/* Camera View */}
      {!permissionDenied && (
        <div className="camera-frame relative aspect-video overflow-hidden rounded-2xl">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            autoPlay
            playsInline
            muted
          />
          <canvas ref={canvasRef} className="hidden" />
          
          {/* Capture Overlay */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-48 h-48 border-2 border-white/50 rounded-lg pointer-events-auto" />
          </div>
          
          {/* Controls */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3">
            <button
              onClick={switchCamera}
              className="p-3 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors"
              aria-label="Switch camera"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18v-6m6 6H6" />
              </svg>
            </button>
            <button
              onClick={capturePhoto}
              disabled={loading}
              className="p-4 bg-white rounded-full shadow-xl hover:bg-gray-100 transition-colors disabled:opacity-50"
              aria-label="Capture photo"
            >
              <span className="w-10 h-10 border-4 border-primary-600 rounded-full flex items-center justify-center">
                <span className="w-5 h-5 bg-primary-600 rounded-full" />
              </span>
            </button>
            <button
              onClick={stopCamera}
              className="p-3 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors"
              aria-label="Close camera"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
      
      {/* Upload Fallback */}
      <div className="upload-zone rounded-2xl border-2 border-dashed border-gray-300 p-8 text-center">
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
          disabled={loading}
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="mt-2 text-gray-600">
            <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
          </p>
          <p className="text-sm text-gray-500 mt-1">JPEG, PNG, WebP • Max 5MB</p>
        </label>
      </div>
      
      {permissionDenied && (
        <p className="text-center text-sm text-red-600" role="alert">
          Camera access denied. Please use file upload above.
        </p>
      )}
    </div>
  )
}