import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { uploadDocument } from '../services/api'

export default function FileUpload({ onUploadComplete }) {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setResult(null)
    setError(null)

    try {
      const response = await uploadDocument(file)
      setResult(response)
      if (onUploadComplete) onUploadComplete(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }, [onUploadComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: uploading,
  })

  const categoryColors = {
    legal: 'from-amber-500 to-orange-600',
    medical: 'from-emerald-500 to-teal-600',
    technical: 'from-blue-500 to-cyan-600',
    financial: 'from-violet-500 to-purple-600',
    general: 'from-gray-500 to-slate-600',
  }

  return (
    <div className="space-y-6">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
                   transition-all duration-300 group
                   ${isDragActive 
                     ? 'dropzone-active border-primary-500 bg-primary-500/5' 
                     : 'border-dark-600 hover:border-primary-500/50 hover:bg-dark-800/30'
                   }
                   ${uploading ? 'opacity-60 pointer-events-none' : ''}`}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {uploading ? (
            <>
              <Loader2 className="w-16 h-16 text-primary-400 animate-spin" />
              <div>
                <p className="text-lg font-semibold text-dark-200">Processing document...</p>
                <p className="text-sm text-dark-400 mt-1">Extracting, classifying, and embedding</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 
                            flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Upload className="w-10 h-10 text-primary-400" />
              </div>
              <div>
                <p className="text-lg font-semibold text-dark-200">
                  {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF here'}
                </p>
                <p className="text-sm text-dark-400 mt-1">
                  or <span className="text-primary-400 font-medium">browse files</span> to upload
                </p>
                <p className="text-xs text-dark-500 mt-3">Supports PDF files only</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Success Result */}
      {result && (
        <div className="glass-card p-6 animate-slide-up">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-emerald-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-dark-100">Upload Successful!</h3>
              <p className="text-sm text-dark-400 mt-1">{result.message}</p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">
                <div className="bg-dark-800/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-dark-500 mb-1">File</p>
                  <p className="text-sm font-medium text-dark-200 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    {result.filename}
                  </p>
                </div>
                <div className="bg-dark-800/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-dark-500 mb-1">Category</p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
                                  bg-gradient-to-r ${categoryColors[result.category] || categoryColors.general} text-white`}>
                    {result.category}
                  </span>
                </div>
                <div className="bg-dark-800/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-dark-500 mb-1">Chunks</p>
                  <p className="text-sm font-medium text-dark-200">{result.chunk_count} chunks</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="glass-card p-6 border-red-500/30 animate-slide-up">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-500/15 flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <h3 className="font-semibold text-red-300">Upload Failed</h3>
              <p className="text-sm text-dark-400 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
