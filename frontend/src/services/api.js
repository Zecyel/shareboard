import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const documentApi = {
  // Get all documents
  getDocuments: () => api.get('/documents'),
  
  // Get a specific document
  getDocument: (id) => api.get(`/documents/${id}`),
  
  // Create a new document
  createDocument: (document) => api.post('/documents', document),
  
  // Update a document
  updateDocument: (id, document) => api.put(`/documents/${id}`, document),
  
  // Delete a document
  deleteDocument: (id) => api.delete(`/documents/${id}`)
}

export default api