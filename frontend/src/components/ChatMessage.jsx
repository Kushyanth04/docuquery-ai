import ReactMarkdown from 'react-markdown'
import { User, Brain, FileText, ChevronDown, ChevronUp, Zap } from 'lucide-react'
import { useState } from 'react'

export default function ChatMessage({ message }) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-9 h-9 rounded-xl flex-shrink-0 flex items-center justify-center
                      ${isUser 
                        ? 'bg-gradient-to-br from-primary-500 to-purple-600' 
                        : 'bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/30'
                      }`}>
        {isUser 
          ? <User className="w-4.5 h-4.5 text-white" /> 
          : <Brain className="w-4.5 h-4.5 text-emerald-400" />
        }
      </div>

      {/* Message Content */}
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Label */}
        <p className={`text-xs font-medium mb-1.5 ${isUser ? 'text-right text-primary-400' : 'text-emerald-400'}`}>
          {isUser ? 'You' : 'DocuQuery AI'}
          {message.cached && (
            <span className="inline-flex items-center gap-1 ml-2 text-amber-400">
              <Zap className="w-3 h-3" /> Cached
            </span>
          )}
        </p>

        {/* Bubble */}
        <div className={isUser ? 'chat-bubble-user px-5 py-3' : 'chat-bubble-ai px-5 py-3'}>
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1.5 text-xs font-medium text-dark-400 
                       hover:text-primary-400 transition-colors duration-200"
            >
              <FileText className="w-3.5 h-3.5" />
              {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
              {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showSources && (
              <div className="mt-2 space-y-2 animate-fade-in">
                {message.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="bg-dark-800/60 border border-dark-600/50 rounded-xl px-4 py-3"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-medium text-primary-400 flex items-center gap-1.5">
                        <FileText className="w-3 h-3" />
                        {source.source}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-dark-500">Page {source.page}</span>
                        {source.score && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-primary-500/15 text-primary-400">
                            {(source.score * 100).toFixed(0)}% match
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-dark-400 leading-relaxed">{source.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
