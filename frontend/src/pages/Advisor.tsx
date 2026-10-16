import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { adviceApi } from '../api/client'
import { AdviceResponse } from '../types'

export function Advisor() {
  const [advice, setAdvice] = useState<AdviceResponse | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{role: string, content: string}>>([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'cards' | 'chat'>('cards')
  
  const generateMutation = useMutation({
    mutationFn: () => adviceApi.get(false),
    onSuccess: (response) => {
      setAdvice(response.data)
    },
  })
  
  const chatMutation = useMutation({
    mutationFn: (messages: Array<{role: string, content: string}>) => adviceApi.chat(messages),
    onMutate: () => setChatLoading(true),
    onSuccess: (response) => {
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.data.message.content }])
      setChatLoading(false)
    },
    onError: () => {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
      setChatLoading(false)
    },
  })
  
  const handleGenerate = () => {
    generateMutation.mutate()
  }
  
  const sendMessage = (content: string) => {
    const trimmedContent = content.trim()
    if (!trimmedContent || chatLoading) return
    
    const userMessage = { role: 'user', content: trimmedContent }
    setChatMessages(prev => [...prev, userMessage])
    setChatInput('')
    
    chatMutation.mutate([...chatMessages, userMessage])
  }

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(chatInput)
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">AI Advisor</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('cards')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'cards' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Advice Cards
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'chat' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Chat
          </button>
        </div>
      </div>
      
      {activeTab === 'cards' && (
        <div className="space-y-6">
          {/* Generate Button */}
          {!advice && (
            <Card className="p-8 text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
                🤖
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Get AI Recommendations</h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                The advisor analyzes your scan history and the digital twin metrics to provide personalized, grounded recommendations for improving waste diversion.
              </p>
              <Button onClick={handleGenerate} disabled={generateMutation.isPending} className="w-full max-w-xs">
                {generateMutation.isPending ? 'Generating...' : 'Generate Advice'}
              </Button>
              {generateMutation.isError && (
                <p className="mt-4 text-red-600 text-sm">Failed to generate advice. Please try again.</p>
              )}
            </Card>
          )}
          
          {/* Advice Cards */}
          {advice && (
            <div className="space-y-6">
              {/* Summary */}
              <Card className="p-6 border-l-4 border-primary-500">
                <h2 className="font-semibold text-gray-900 mb-2">Summary</h2>
                <p className="text-gray-600">{advice.summary}</p>
                {advice.cached && (
                  <p className="text-sm text-amber-600 mt-2">⚠️ Showing cached advice (LLM unavailable)</p>
                )}
              </Card>
              
              {/* Issues */}
              {advice.issues.length > 0 && (
                <Card className="p-6 border-l-4 border-red-500">
                  <h2 className="font-semibold text-gray-900 mb-3">Issues Identified</h2>
                  <ul className="space-y-2">
                    {advice.issues.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-600">
                        <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        {issue}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
              
              {/* Actions */}
              <Card className="p-6">
                <h2 className="font-semibold text-gray-900 mb-4">Recommended Actions</h2>
                <div className="space-y-3">
                  {advice.actions.map((action, i) => (
                    <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{action.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{action.why}</p>
                          <div className="flex items-center gap-3 mt-2">
                            <span className={`px-2 py-0.5 text-xs rounded-full ${
                              action.effort === 'low' ? 'bg-green-100 text-green-700' :
                              action.effort === 'medium' ? 'bg-amber-100 text-amber-700' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {action.effort} effort
                            </span>
                            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded-full">
                              {action.owner}
                            </span>
                          </div>
                        </div>
                        <span className="text-sm text-green-600 font-medium whitespace-nowrap">{action.expected_impact}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Reuse Ideas */}
              {advice.reuse_ideas.length > 0 && (
                <Card className="p-6 border-l-4 border-green-500">
                  <h2 className="font-semibold text-gray-900 mb-3">Reuse & Upcycling Ideas</h2>
                  <ul className="space-y-2">
                    {advice.reuse_ideas.map((idea, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-600">
                        <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        {idea}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
              
              {/* Disclaimer */}
              <p className="text-xs text-gray-500 text-center">{advice.disclaimer}</p>
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'chat' && (
        <Card className="p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Chat with Advisor</h2>
          <p className="text-sm text-gray-500 mb-4">
            Ask about recycling, reuse, repair, upcycling, or circular economy topics.
          </p>
          
          {/* Messages */}
          <div className="h-96 overflow-y-auto space-y-4 mb-4 border border-gray-200 rounded-lg p-4 bg-gray-50">
            {chatMessages.length === 0 && (
              <p className="text-gray-500 text-center text-sm">Start a conversation...</p>
            )}
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-primary-600 text-white rounded-br-none' 
                    : 'bg-white text-gray-900 rounded-bl-none shadow-sm'
                }`}>
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>
          
          {/* Input */}
          <form onSubmit={handleChatSubmit} className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask about recycling, reuse, upcycling..."
              className="flex-1 input"
              disabled={chatLoading}
            />
            <Button type="submit" disabled={chatLoading || !chatInput.trim()}>
              {chatLoading ? 'Sending...' : 'Send'}
            </Button>
          </form>
          
          {/* Suggested Prompts */}
          <div className="mt-4 flex flex-wrap gap-2">
            {[
              'How do I recycle pizza boxes?',
              'What can I upcycle from glass jars?',
              'Where do batteries go?',
              'How to reduce contamination?',
            ].map((prompt, i) => (
              <button
                key={i}
                onClick={() => {
                  setChatInput(prompt)
                  sendMessage(prompt)
                }}
                className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}