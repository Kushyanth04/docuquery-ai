import { useState, useEffect } from 'react'
import { FileText, Trash2, Clock, Tag, Layers, ChevronRight } from 'lucide-react'
import { getDocuments, deleteDocument } from '../services/api'

export default function Sidebar({ onSelectDocument, selectedDocId }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleDelete = async (e, docId) => {
    e.stopPropagation()
    if (!confirm('Delete this document?')) return

    try {
      await deleteDocument(docId)
      setDocuments(documents.filter(d => d.document_id !== docId))
      if (selectedDocId === docId && onSelectDocument) {
        onSelectDocument(null)
      }
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  const categoryColors = {
    legal: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    medical: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    technical: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    financial: 'bg-violet-500/15 text-violet-400 border-violet-500/30',
    general: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown'
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="w-72 glass border-r border-dark-700/50 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-700/50">
        <h2 className="text-sm font-semibold text-dark-200 flex items-center gap-2">
          <Layers className="w-4 h-4 text-primary-400" />
          Documents ({documents.length})
        </h2>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {/* All Documents Option */}
        <button
          onClick={() => onSelectDocument && onSelectDocument(null)}
          className={`w-full text-left px-3 py-2.5 rounded-xl transition-all duration-200 group
                    ${!selectedDocId 
                      ? 'bg-primary-500/10 border border-primary-500/30' 
                      : 'hover:bg-dark-700/50 border border-transparent'
                    }`}
        >
          <span className="text-sm font-medium text-dark-200">All Documents</span>
        </button>

        {loading ? (
          <div className="space-y-2 p-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="loading-shimmer h-20 rounded-xl" />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 px-4">
            <FileText className="w-10 h-10 text-dark-600 mx-auto mb-3" />
            <p className="text-sm text-dark-500">No documents yet</p>
            <p className="text-xs text-dark-600 mt-1">Upload a PDF to get started</p>
          </div>
        ) : (
          documents.map((doc) => (
            <button
              key={doc.document_id}
              onClick={() => onSelectDocument && onSelectDocument(doc)}
              className={`w-full text-left px-3 py-3 rounded-xl transition-all duration-200 group
                        ${selectedDocId === doc.document_id 
                          ? 'bg-primary-500/10 border border-primary-500/30' 
                          : 'hover:bg-dark-700/50 border border-transparent'
                        }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-dark-200 truncate flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-dark-400 flex-shrink-0" />
                    {doc.filename}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border
                                    ${categoryColors[doc.category] || categoryColors.general}`}>
                      <Tag className="w-2.5 h-2.5" />
                      {doc.category}
                    </span>
                    <span className="text-[10px] text-dark-500">{doc.chunk_count} chunks</span>
                  </div>
                  <p className="text-[10px] text-dark-600 mt-1 flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    {formatDate(doc.created_at)}
                  </p>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => handleDelete(e, doc.document_id)}
                    className="p-1.5 rounded-lg hover:bg-red-500/15 text-dark-500 hover:text-red-400 transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <ChevronRight className="w-3.5 h-3.5 text-dark-600" />
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  )
}
