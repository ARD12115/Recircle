import { create } from 'zustand'

interface ScanSessionState {
  image: File | null
  previewUrl: string | null
  result: any | null
  loading: boolean
  error: string | null
  setImage: (file: File | null) => void
  setPreviewUrl: (url: string | null) => void
  setResult: (result: any) => void
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