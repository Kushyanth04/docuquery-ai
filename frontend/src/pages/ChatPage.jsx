import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Brain, Sparkles } from 'lucide-react'
import ChatMessage from '../components/ChatMessage'
import Sidebar from '../components/Sidebar'
import { askQuestion, askQuestionStream } from '../services/api'

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setLoading(true)

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: question }])

    // Add loading AI message
    const aiMsgId = Date.now()
    setMessages(prev => [...prev, {
      id: aiMsgId,
      role: 'assistant',
      content: '',
      sources: [],
      loading: true,
    }])

    try {
      // Try streaming first
      let fullAnswer = ''
      let sources = []

      await askQuestionStream(
        question,
        selectedDoc?.document_id,
        selectedDoc?.category,
        // onChunk
        (chunk) => {
          fullAnswer += chunk
          setMessages(prev => prev.map(m =>
            m.id === aiMsgId ? { ...m, content: fullAnswer, loading: false } : m
          ))
        },
        // onSources
        (srcData) => {
          sources = srcData
          setMessages(prev => prev.map(m =>
            m.id === aiMsgId ? { ...m, sources: srcData } : m
          ))
        },
        // onDone
        (cached) => {
          setMessages(prev => prev.map(m =>
            m.id === aiMsgId ? { ...m, cached, loading: false } : m
          ))
        },
      )
    } catch (err) {
      // Fallback to non-streaming
      try {
        const response = await askQuestion(
          question,
          selectedDoc?.document_id,
          selectedDoc?.category,
        )
        setMessages(prev => prev.map(m =>
          m.id === aiMsgId ? {
            ...m,
            content: response.answer,
            sources: response.sources,
            cached: response.cached,
            loading: false,
          } : m
        ))
      } catch (fallbackErr) {
        setMessages(prev => prev.map(m =>
          m.id === aiMsgId ? {
            ...m,
            content: `Sorry, I encountered an error: ${fallbackErr.message}`,
            loading: false,
          } : m
        ))
      }
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleSelectDocument = (doc) => {
    setSelectedDoc(doc)
  }

  const suggestedQuestions = [
    "What is the main topic of this document?",
    "Summarize the key points",
    "What are the conclusions?",
    "List all important dates mentioned",
  ]

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Sidebar */}
      <Sidebar
        onSelectDocument={handleSelectDocument}
        selectedDocId={selectedDoc?.document_id}
      />

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="px-6 py-3 border-b border-dark-700/50 glass">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 
                          border border-emerald-500/30 flex items-center justify-center">
              <Brain className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-dark-100">DocuQuery AI Chat</h2>
              <p className="text-xs text-dark-500">
                {selectedDoc 
                  ? `Querying: ${selectedDoc.filename} (${selectedDoc.category})`
                  : 'Searching all documents'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-500/15 to-purple-500/15 
                            border border-primary-500/20 flex items-center justify-center mb-6 animate-float">
                <Sparkles className="w-10 h-10 text-primary-400" />
              </div>
              <h2 className="text-xl font-bold text-dark-200 mb-2">Ask anything about your documents</h2>
              <p className="text-dark-400 text-sm max-w-md mb-8">
                Upload a PDF and ask questions. DocuQuery AI will find relevant passages 
                and generate accurate answers with source citations.
              </p>

              {/* Suggested Questions */}
              <div className="grid grid-cols-2 gap-2 max-w-lg">
                {suggestedQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(q)}
                    className="text-left text-xs text-dark-400 bg-dark-800/40 border border-dark-700/50 
                             rounded-xl px-4 py-3 hover:border-primary-500/30 hover:text-dark-300 
                             hover:bg-dark-700/30 transition-all duration-200"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id || idx}>
                {msg.loading ? (
                  <div className="flex gap-3 animate-slide-up">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 
                                  border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-4.5 h-4.5 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-emerald-400 mb-1.5">DocuQuery AI</p>
                      <div className="chat-bubble-ai px-5 py-3">
                        <div className="flex items-center gap-2 text-dark-400">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span className="text-sm">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <ChatMessage message={msg} />
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="px-6 py-4 border-t border-dark-700/50 glass">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              ref={inputRef}
              id="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={loading}
              className="input-field flex-1"
              autoComplete="off"
            />
            <button
              id="send-button"
              type="submit"
              disabled={loading || !input.trim()}
              className="btn-primary px-4 flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
