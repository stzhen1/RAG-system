import type {
  ChatRequest,
  DocumentUploadResponse,
  DocumentStatus,
} from '../types'

const API_BASE = '/api'

export async function* chatStream(
  request: ChatRequest,
): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`)
  }

  const { parseSSEStream } = await import('../lib/utils')
  yield* parseSSEStream(response)
}

export async function uploadDocument(
  file: File,
): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || 'Upload failed')
  }

  return response.json()
}

export async function getDocumentStatus(
  documentId: string,
): Promise<DocumentStatus> {
  const response = await fetch(`${API_BASE}/documents/${documentId}/status`)

  if (!response.ok) {
    throw new Error(`Status check failed: ${response.status}`)
  }

  return response.json()
}
