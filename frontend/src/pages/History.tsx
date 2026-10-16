import { useQuery } from '@tanstack/react-query'
import { Card } from '../../components/ui/Card'
import { scanApi } from '../../api/client'
import { ScanHistoryItem } from '../../types'
import { format } from 'date-fns'

export function History() {
  const { data, isLoading } = useQuery({
    queryKey: ['scans'],
    queryFn: () => scanApi.history(),
  })
  
  const scans = (data?.data as any)?.scans || []
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Scan History</h1>
      
      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => (
            <Card key={i} className="p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
              <div className="h-3 bg-gray-200 rounded w-1/2" />
            </Card>
          ))}
        </div>
      ) : scans.length === 0 ? (
        <Card className="p-8 text-center">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h2 className="text-lg font-medium text-gray-900 mb-1">No scans yet</h2>
          <p className="text-gray-500">Your scan history will appear here</p>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {scans.map((scan: ScanHistoryItem) => (
                <tr key={scan.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {format(new Date(scan.created_at), 'MMM d, yyyy HH:mm')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {scan.subtype}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${
                      scan.predicted_class === 'recyclable' ? 'badge-recyclable' :
                      scan.predicted_class === 'reusable' ? 'badge-reusable' :
                      scan.predicted_class === 'biodegradable' ? 'badge-biodegradable' :
                      scan.predicted_class === 'hazardous' ? 'badge-hazardous' :
                      'badge-residual'
                    }`}>
                      {scan.predicted_class}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {Math.round(scan.confidence * 100)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {scan.confirmed_bin || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}