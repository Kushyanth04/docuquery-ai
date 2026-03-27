const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Make an authenticated API request to the backend.
 */
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token')

  const headers = {
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response
}

// ==================== Auth ====================

export async function signup(email, password) {
  const response = await apiRequest('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  return response.json()
}

export async function login(email, password) {
  const response = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  const data = await response.json()

  if (data.session?.access_token) {
    localStorage.setItem('access_token', data.session.access_token)
    localStorage.setItem('refresh_token', data.session.refresh_token)
  }

  return data
}

export async function getMe() {
  const response = await apiRequest('/auth/me')
  return response.json()
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  window.location.href = '/login'
}

export function isAuthenticated() {
  return !!localStorage.getItem('access_token')
}

// ==================== Documents ====================

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiRequest('/documents/upload', {
    method: 'POST',
    body: formData,
  })
  return response.json()
}

export async function getDocuments() {
  const response = await apiRequest('/documents/history')
  return response.json()
}

export async function deleteDocument(documentId) {
  const response = await apiRequest(`/documents/${documentId}`, {
    method: 'DELETE',
  })
  return response.json()
}

// ==================== Query ====================

export async function askQuestion(question, documentId = null, namespace = null) {
  const response = await apiRequest('/query/', {
    method: 'POST',
    body: JSON.stringify({
      question,
      document_id: documentId,
      namespace,
      top_k: 5,
    }),
  })
  return response.json()
}

export async function askQuestionStream(question, documentId = null, namespace = null, onChunk, onSources, onDone) {
  const token = localStorage.getItem('access_token')

  const response = await fetch(`${API_BASE}/query/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      document_id: documentId,
      namespace,
      top_k: 5,
    }),
  })

  if (!response.ok) throw new Error('Stream request failed')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'sources' && onSources) onSources(data.data)
          if (data.type === 'chunk' && onChunk) onChunk(data.data)
          if (data.type === 'answer' && onChunk) onChunk(data.data)
          if (data.type === 'done' && onDone) onDone(data.cached)
        } catch (e) {
          console.warn('Failed to parse SSE:', e)
        }
      }
    }
  }
}

// ==================== Classification ====================

export async function classifyText(text) {
  const response = await apiRequest('/classify/', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
  return response.json()
}

// ==================== Chat History ====================

export async function getChatHistory(documentId = null) {
  const params = documentId ? `?document_id=${documentId}` : ''
  const response = await apiRequest(`/query/history${params}`)
  return response.json()
}
