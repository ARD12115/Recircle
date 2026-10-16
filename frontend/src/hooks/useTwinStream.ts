import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { twinApi } from '../../api/client'

export function useTwinStream(onMessage: (event: MessageEvent) => void) {
  const eventSourceRef = useRef<EventSource | null>(null)
  const [connected, setConnected] = useState(false)
  const [reconnecting, setReconnecting] = useState(false)
  
  useEffect(() => {
    let reconnectAttempts = 0
    const maxReconnectAttempts = 5
    const reconnectDelay = 3000
    
    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
      
      const es = new EventSource(twinApi.stream())
      eventSourceRef.current = es
      
      es.onopen = () => {
        setConnected(true)
        setReconnecting(false)
        reconnectAttempts = 0
      }
      
      es.onerror = () => {
        setConnected(false)
        if (reconnectAttempts < maxReconnectAttempts) {
          setReconnecting(true)
          reconnectAttempts++
          setTimeout(connect, reconnectDelay)
        }
      }
      
      es.addEventListener('scan.created', onMessage)
      es.addEventListener('metrics.updated', onMessage)
      es.addEventListener('twin.tick', onMessage)
    }
    
    connect()
    
    // Fallback polling
    const pollInterval = setInterval(() => {
      if (!connected) {
        // Could trigger a refetch here
      }
    }, 3000)
    
    return () => {
      clearInterval(pollInterval)
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [onMessage])
  
  return { connected, reconnecting }
}