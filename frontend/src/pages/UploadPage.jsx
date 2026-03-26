import { Upload, Brain, FileSearch, Zap, Shield, BarChart3 } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import { useNavigate } from 'react-router-dom'

export default function UploadPage() {
  const navigate = useNavigate()

  const handleUploadComplete = (result) => {
    // Navigate to chat after successful upload  
    setTimeout(() => navigate('/chat'), 2000)
  }

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Automatic document classification using ML',
      color: 'from-primary-500/20 to-purple-500/20 border-primary-500/30',
      iconColor: 'text-primary-400',
    },
    {
      icon: FileSearch,
      title: 'Smart Chunking',
      description: 'LangChain text splitting for optimal retrieval',
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30',
      iconColor: 'text-emerald-400',
    },
    {
      icon: Zap,
      title: 'Vector Embeddings',
      description: 'Semantic search with HuggingFace transformers',
      color: 'from-amber-500/20 to-orange-500/20 border-amber-500/30',
      iconColor: 'text-amber-400',
    },
    {
      icon: Shield,
      title: 'Secure Storage',
      description: 'Encrypted storage with Supabase',
      color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
      iconColor: 'text-blue-400',
    },
    {
      icon: BarChart3,
      title: 'Auto Classification',
      description: 'TF-IDF + Naive Bayes categorization',
      color: 'from-violet-500/20 to-fuchsia-500/20 border-violet-500/30',
      iconColor: 'text-violet-400',
    },
  ]

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl 
                      bg-gradient-to-br from-primary-500/20 to-purple-500/20 
                      border border-primary-500/30 mb-4">
          <Upload className="w-7 h-7 text-primary-400" />
        </div>
        <h1 className="text-2xl font-bold text-dark-100">Upload Document</h1>
        <p className="text-dark-400 mt-2 max-w-md mx-auto">
          Upload a PDF and our AI will extract, classify, and index it for intelligent Q&A
        </p>
      </div>

      {/* Upload Component */}
      <FileUpload onUploadComplete={handleUploadComplete} />

      {/* Features Grid */}
      <div>
        <h2 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 text-center">
          Processing Pipeline
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="glass-card p-4 text-center group"
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${feature.color} 
                            flex items-center justify-center mx-auto mb-3
                            group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-5 h-5 ${feature.iconColor}`} />
              </div>
              <h3 className="text-xs font-semibold text-dark-200">{feature.title}</h3>
              <p className="text-[10px] text-dark-500 mt-1">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
