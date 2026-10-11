import React, { useState, useEffect, useRef } from 'react'
import { ChatMessage } from '../../types'
import { chatAPI } from '../../services/api'
import { Send, Bot, User, Sparkles, Info, Loader2 } from 'lucide-react'
import Button from '../ui/Button'
import toast from 'react-hot-toast'

export interface ChatPanelProps {
  reportId: string
  suggestions?: string[]
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ reportId, suggestions = [] }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your AI Analyst. Ask me anything about this dataset—trends, specific queries, anomalies, or summaries.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatSuggestions, setChatSuggestions] = useState<string[]>(suggestions)
  const [showTooltip, setShowTooltip] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Load chat history and suggestions if available
    const loadHistory = async () => {
      try {
        const historyRes = await chatAPI.history(reportId)
        if (historyRes.data && historyRes.data.length > 0) {
          setMessages(historyRes.data)
        }
      } catch {
        // First time or empty history
      }

      if (suggestions.length === 0) {
        try {
          const sugRes = await chatAPI.suggestions(reportId)
          if (sugRes.data && Array.isArray(sugRes.data)) {
            setChatSuggestions(sugRes.data)
          }
        } catch {
          // Defaults
          setChatSuggestions([
            'What is the key takeaway from this dataset?',
            'Are there any anomalies or outliers?',
            'What are the highest and lowest performing segments?',
          ])
        }
      }
    }

    if (reportId) {
      loadHistory()
    }
  }, [reportId, suggestions])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = async (messageText: string) => {
    const text = messageText.trim()
    if (!text || isLoading) return

    const userMsg: ChatMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const res = await chatAPI.send(reportId, text)
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.data.response || res.data.message || res.data.content,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: res.data.sources,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      toast.error('AI assistant is currently unavailable. Showing dataset summary fallback.')
      const fallbackMsg: ChatMessage = {
        role: 'assistant',
        content: 'I could not connect to the remote AI service at this moment. You can continue reviewing the generated KPI cards, automated insights, and visual charts directly in the report.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, fallbackMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend(input)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200/80 shadow-sm flex flex-col h-[580px] overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
              AI Analyst
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </h3>
            <p className="text-[11px] text-gray-500">Ask questions regarding your data</p>
          </div>
        </div>

        <div className="relative">
          <button
            type="button"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            <Info className="w-4 h-4" />
          </button>
          {showTooltip && (
            <div className="absolute right-0 top-7 w-64 bg-gray-900 text-white text-xs p-2.5 rounded-lg shadow-lg z-20">
              The AI Analyst queries the statistical profile and insights generated from your uploaded spreadsheet.
            </div>
          )}
        </div>
      </div>

      {/* Suggested chips */}
      {chatSuggestions.length > 0 && (
        <div className="p-3 border-b border-gray-100 bg-white flex items-center gap-2 overflow-x-auto text-xs no-scrollbar">
          <Sparkles className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 ml-1" />
          {chatSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(suggestion)}
              disabled={isLoading}
              className="px-3 py-1 bg-blue-50/80 hover:bg-blue-100/80 text-blue-700 rounded-full border border-blue-200/60 whitespace-nowrap transition-colors text-xs flex-shrink-0 disabled:opacity-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user'
          return (
            <div
              key={index}
              className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs ${
                  isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                  isUser
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-900 rounded-bl-none'
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200/60 text-[11px] text-gray-500">
                    <span className="font-semibold">Sources: </span>
                    {msg.sources.join(', ')}
                  </div>
                )}

                {msg.timestamp && (
                  <p
                    className={`text-[10px] mt-1 text-right ${
                      isUser ? 'text-blue-200' : 'text-gray-400'
                    }`}
                  >
                    {msg.timestamp}
                  </p>
                )}
              </div>
            </div>
          )
        })}

        {isLoading && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3 text-sm text-gray-500 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span>Analyzing data...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="p-3 border-t border-gray-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend(input)
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about this report..."
            disabled={isLoading}
            className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-colors"
          />
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            size="md"
            className="px-4 py-2.5 rounded-xl flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}

export default ChatPanel
