<template>
  <div id="app">
    <div class="app-layout">
      <div class="document-list">
        <div class="document-list-header">
          <h3>Shared Documents</h3>
          <button @click="createNewDocument" class="create-btn">+ New Document</button>
        </div>
        <div class="document-items">
          <div
            v-for="document in documents"
            :key="document.id"
            class="document-item"
            :class="{ active: selectedDocumentId === document.id }"
            @click="selectDocument(document.id)"
          >
            <div class="document-title">{{ document.title || 'Untitled Document' }}</div>
            <div class="document-date">{{ formatDate(document.updated_at) }}</div>
          </div>
          <div v-if="documents.length === 0" class="no-documents">
            No documents yet. Create your first document!
          </div>
        </div>
      </div>

      <div class="monaco-editor-container">
        <div class="editor-header" v-if="currentDocument">
          <input
            v-model="documentTitle"
            @blur="updateTitle"
            class="document-title-input"
            placeholder="Document title..."
          />
          <div class="editor-actions">
            <button @click="saveDocument" class="save-btn" :disabled="!hasChanges">
              {{ isSaving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>

        <div ref="editorContainer" class="editor-container"></div>

        <div v-if="!currentDocument" class="no-document-selected">
          <h2>Welcome to Shareboard</h2>
          <p>Select a document from the left panel or create a new one to get started.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as monaco from 'monaco-editor'
import { documentApi } from './services/api'
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'

self.MonacoEnvironment = {
  getWorker(_, label) {
    return new EditorWorker()
  }
}

// State
const documents = ref([])
const selectedDocumentId = ref(null)
const editor = ref(null)
const editorContainer = ref(null)
const currentDocument = ref(null)
const documentTitle = ref('')
const hasChanges = ref(false)
const isSaving = ref(false)
const originalContent = ref('')

// Watchers
watch(selectedDocumentId, async (newId) => {
  if (newId) {
    await loadDocument(newId)
  } else {
    currentDocument.value = null
    documentTitle.value = ''
    if (editor.value) {
      editor.value.setValue('')
    }
    hasChanges.value = false
    originalContent.value = ''
  }
})

// Lifecycle
onMounted(async () => {
  await loadDocuments()
  initializeEditor()
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.dispose()
  }
})

// Methods
async function loadDocuments() {
  try {
    const response = await documentApi.getDocuments()
    documents.value = response.data
  } catch (error) {
    console.error('Error loading documents:', error)
  }
}

async function createNewDocument() {
  try {
    const response = await documentApi.createDocument({
      title: 'New Document',
      content: ''
    })
    await loadDocuments()
    selectDocument(response.data.id)
  } catch (error) {
    console.error('Error creating document:', error)
  }
}

function selectDocument(documentId) {
  selectedDocumentId.value = documentId
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString()
}

function initializeEditor() {
  if (editorContainer.value) {
    editor.value = monaco.editor.create(editorContainer.value, {
      value: '',
      language: 'markdown',
      theme: 'vs-light',
      automaticLayout: true,
      wordWrap: 'on',
      minimap: { enabled: false }
    })

    editor.value.onDidChangeModelContent(() => {
      const currentContent = editor.value.getValue()
      hasChanges.value = currentContent !== originalContent.value
    })
  }
}

async function loadDocument(documentId) {
  try {
    const response = await documentApi.getDocument(documentId)
    currentDocument.value = response.data
    documentTitle.value = response.data.title
    originalContent.value = response.data.content

    if (editor.value) {
      editor.value.setValue(response.data.content)
    }

    hasChanges.value = false
  } catch (error) {
    console.error('Error loading document:', error)
  }
}

async function saveDocument() {
  if (!currentDocument.value || isSaving.value) return
  isSaving.value = true
  try {
    const content = editor.value.getValue()
    await documentApi.updateDocument(currentDocument.value.id, {
      title: documentTitle.value,
      content: content
    })
    originalContent.value = content
    hasChanges.value = false
    await loadDocuments()
  } catch (error) {
    console.error('Error saving document:', error)
  } finally {
    isSaving.value = false
  }
}

async function updateTitle() {
  if (!currentDocument.value || !documentTitle.value.trim()) return
  try {
    await documentApi.updateDocument(currentDocument.value.id, {
      title: documentTitle.value.trim()
    })
    await loadDocuments()
  } catch (error) {
    console.error('Error updating title:', error)
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f8f9fa;
}

#app {
  height: 100vh;
  overflow: hidden;
}

.app-layout {
  display: flex;
  height: 100vh;
}

/* Document list styles */
.document-list {
  width: 300px;
  background: #f5f5f5;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.document-list-header {
  padding: 20px;
  border-bottom: 1px solid #ddd;
  background: white;
}

.document-list-header h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.create-btn {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.create-btn:hover {
  background: #0056b3;
}

.document-items {
  flex: 1;
  overflow-y: auto;
}

.document-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.document-item:hover {
  background: #e9ecef;
}

.document-item.active {
  background: #007bff;
  color: white;
}

.document-title {
  font-weight: 500;
  margin-bottom: 5px;
}

.document-date {
  font-size: 12px;
  opacity: 0.7;
}

.no-documents {
  padding: 20px;
  text-align: center;
  color: #666;
  font-style: italic;
}

/* Editor styles */
.monaco-editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #ddd;
}

.document-title-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  margin-right: 15px;
}

.document-title-input:focus {
  outline: none;
  border-color: #007bff;
}

.editor-actions {
  display: flex;
  gap: 10px;
}

.save-btn {
  padding: 8px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:hover:not(:disabled) {
  background: #218838;
}

.save-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.editor-container {
  flex: 1;
  min-height: 0;
}

.no-document-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #666;
}

.no-document-selected h2 {
  margin-bottom: 10px;
  color: #333;
}
</style>