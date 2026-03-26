import { useState, useEffect } from 'react'
import { FileText, Trash2, Clock, Tag, HardDrive, Layers, AlertCircle } from 'lucide-react'
import { getDocuments, deleteDocument } from '../services/api'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document? This will remove it from the vector database as well.')) return

    try {
      await deleteDocument(docId)
      setDocuments(documents.filter(d => d.document_id !== docId))
    } catch (err) {
      alert('Failed to delete: ' + err.message)
    }
  }

  const categoryColors = {
    legal: 'bg-amber-500/15 text-amber-400',
    medical: 'bg-emerald-500/15 text-emerald-400',
    technical: 'bg-blue-500/15 text-blue-400',
    financial: 'bg-violet-500/15 text-violet-400',
    general: 'bg-gray-500/15 text-gray-400',
  }

  const formatSize = (bytes) => {
    if (!bytes) return 'Unknown'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown'
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="loading-shimmer h-24 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-dark-100 flex items-center gap-3">
            <Layers className="w-7 h-7 text-primary-400" />
            Documents
          </h1>
          <p className="text-dark-400 mt-1">{documents.length} document{documents.length !== 1 ? 's' : ''} uploaded</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl px-4 py-3 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Document Grid */}
      {documents.length === 0 ? (
        <div className="text-center py-16">
          <FileText className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-dark-300">No documents yet</h3>
          <p className="text-dark-500 mt-2">Upload a PDF to get started with document Q&A</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, idx) => (
            <div
              key={doc.document_id}
              className="glass-card p-5 animate-slide-up"
              style={{ animationDelay: `${idx * 0.05}s` }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/15 to-orange-500/15 
                                border border-primary-500/20 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-primary-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-dark-200 truncate">{doc.filename}</h3>
                    <div className="flex flex-wrap items-center gap-3 mt-2">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium
                                      ${categoryColors[doc.category] || categoryColors.general}`}>
                        <Tag className="w-3 h-3" />
                        {doc.category}
                      </span>
                      <span className="text-xs text-dark-500 flex items-center gap-1">
                        <Layers className="w-3 h-3" />
                        {doc.chunk_count} chunks
                      </span>
                      <span className="text-xs text-dark-500 flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        {formatSize(doc.file_size)}
                      </span>
                      <span className="text-xs text-dark-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(doc.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="p-2 rounded-xl hover:bg-red-500/15 text-dark-500 hover:text-red-400 
                           transition-all duration-200"
                  title="Delete document"
                >
                  <Trash2 className="w-4.5 h-4.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
