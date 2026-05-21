export interface ChatRequest {
  query: string
  conversation_id?: string
  history: Array<{ role: string; content: string }>
  filters?: Record<string, string>
}

export interface Citation {
  document_name: string
  page?: number
  content_snippet: string
  score: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  isStreaming?: boolean
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  status: string
  file_size_bytes: number
}

export interface DocumentStatus {
  id: string
  filename: string
  file_type: string
  status:
    | 'uploaded'
    | 'parsing'
    | 'chunking'
    | 'embedding'
    | 'indexing'
    | 'ready'
    | 'failed'
  page_count?: number
  file_size_bytes: number
  error_message?: string
  created_at: string
  updated_at: string
}
