import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { uploadDocument } from '../../api/client'

interface UploadDialogProps {
  open: boolean
  onClose: () => void
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error'

export default function UploadDialog({ open, onClose }: UploadDialogProps) {
  const [state, setState] = useState<UploadState>('idle')
  const [message, setMessage] = useState('')
  const [documentId, setDocumentId] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!open) return null

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setState('uploading')
    setMessage('Uploading...')

    try {
      const result = await uploadDocument(file)
      setState('success')
      setDocumentId(result.document_id)
      setMessage(`"${file.name}" uploaded. Processing started.`)
    } catch (error) {
      setState('error')
      setMessage((error as Error).message)
    }
  }

  const handleReset = () => {
    setState('idle')
    setMessage('')
    setDocumentId('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleClose = () => {
    handleReset()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={handleClose}
      />
      <div className="relative bg-surface border border-border rounded-xl w-full max-w-md p-6 shadow-2xl animate-slide-up">
        <div className="mb-5">
          <h3 className="font-mono text-sm font-medium text-text">
            Upload Document
          </h3>
          <p className="font-mono text-[11px] text-muted mt-1 uppercase">
            PDF &middot; TXT &middot; Markdown &middot; Max 100MB
          </p>
        </div>

        <div className="space-y-4">
          {state === 'idle' && (
            <label className="flex flex-col items-center gap-3 p-8 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-accent/40 transition-colors">
              <Upload className="h-7 w-7 text-muted" />
              <div className="text-center">
                <p className="text-sm text-text font-medium">
                  Select a file to upload
                </p>
                <p className="font-mono text-[11px] text-muted mt-1 uppercase">
                  or drag and drop
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                onChange={handleFile}
                className="hidden"
              />
            </label>
          )}

          {state === 'uploading' && (
            <div className="flex items-center gap-3 p-5 bg-surface border border-border rounded-lg">
              <Loader2 className="h-5 w-5 text-accent animate-spin flex-shrink-0" />
              <p className="text-sm text-text">{message}</p>
            </div>
          )}

          {state === 'success' && (
            <div className="flex items-start gap-3 p-5 bg-accent/5 border border-accent/20 rounded-lg">
              <CheckCircle className="h-5 w-5 text-accent mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-text font-medium">{message}</p>
                <p className="font-mono text-[10px] text-muted mt-1 uppercase">
                  ID: {documentId}
                </p>
              </div>
            </div>
          )}

          {state === 'error' && (
            <div className="flex items-start gap-3 p-5 bg-red-500/5 border border-red-500/20 rounded-lg">
              <XCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-red-300 font-medium">
                  Upload failed
                </p>
                <p className="text-xs text-red-400/70 mt-1">{message}</p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={handleClose}
            className="font-mono text-xs text-muted hover:text-text uppercase tracking-wider transition-colors px-4 py-2"
          >
            {state === 'success' ? 'Done' : 'Cancel'}
          </button>
        </div>
      </div>
    </div>
  )
}
