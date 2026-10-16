import { create } from 'zustand'
import { ScanResult } from '../types'

interface ScanSessionState {
  image: File | null
  previewUrl: string | null
  result: ScanResult | null
  loading: boolean
  error: string | null
  setImage: (file: File | null) => void
  setPreviewUrl: (url: string | null) => void
  setResult: (result: ScanResult | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clear: () => void
}

export const useScanSession = create<ScanSessionState>((set) => ({
  image: null,
  previewUrl: null,
  result: null,
  loading: false,
  error: null,
  setImage: (image) => set({ image }),
  setPreviewUrl: (previewUrl) => set({ previewUrl }),
  setResult: (result) => set({ result, loading: false }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  clear: () => set({ image: null, previewUrl: null, result: null, loading: false, error: null }),
}))