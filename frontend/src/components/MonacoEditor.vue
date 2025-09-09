<template>
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
</template>

<script>
import * as monaco from 'monaco-editor'
import { documentApi } from '../services/api'

// Configure Monaco Editor workers
self.MonacoEnvironment = {
  getWorkerUrl: function (moduleId, label) {
    if (label === 'json') {
      return './monaco-editor/esm/vs/language/json/json.worker.js'
    }
    if (label === 'css' || label === 'scss' || label === 'less') {
      return './monaco-editor/esm/vs/language/css/css.worker.js'
    }
    if (label === 'html' || label === 'handlebars' || label === 'razor') {
      return './monaco-editor/esm/vs/language/html/html.worker.js'
    }
    if (label === 'typescript' || label === 'javascript') {
      return './monaco-editor/esm/vs/language/typescript/ts.worker.js'
    }
    return './monaco-editor/esm/vs/editor/editor.worker.js'
  }
}

export default {
  name: 'MonacoEditor',
  props: {
    documentId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      editor: null,
      currentDocument: null,
      documentTitle: '',
      hasChanges: false,
      isSaving: false,
      originalContent: ''
    }
  },
  watch: {
    documentId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.loadDocument(newId)
        } else {
          this.currentDocument = null
          this.documentTitle = ''
          if (this.editor) {
            this.editor.setValue('')
          }
        }
      }
    }
  },
  mounted() {
    this.initializeEditor()
  },
  beforeUnmount() {
    if (this.editor) {
      this.editor.dispose()
    }
  },
  methods: {
    initializeEditor() {
      if (this.$refs.editorContainer) {
        this.editor = monaco.editor.create(this.$refs.editorContainer, {
          value: '',
          language: 'markdown',
          theme: 'vs-light',
          automaticLayout: true,
          wordWrap: 'on',
          minimap: { enabled: false }
        })

        // Listen for content changes
        this.editor.onDidChangeModelContent(() => {
          const currentContent = this.editor.getValue()
          this.hasChanges = currentContent !== this.originalContent
        })
      }
    },

    async loadDocument(documentId) {
      try {
        const response = await documentApi.getDocument(documentId)
        this.currentDocument = response.data
        this.documentTitle = response.data.title
        this.originalContent = response.data.content
        
        if (this.editor) {
          this.editor.setValue(response.data.content)
        }
        
        this.hasChanges = false
      } catch (error) {
        console.error('Error loading document:', error)
      }
    },

    async saveDocument() {
      if (!this.currentDocument || this.isSaving) return

      this.isSaving = true
      try {
        const content = this.editor.getValue()
        await documentApi.updateDocument(this.currentDocument.id, {
          title: this.documentTitle,
          content: content
        })
        
        this.originalContent = content
        this.hasChanges = false
        this.$emit('documentSaved')
      } catch (error) {
        console.error('Error saving document:', error)
      } finally {
        this.isSaving = false
      }
    },

    async updateTitle() {
      if (!this.currentDocument || !this.documentTitle.trim()) return
      
      try {
        await documentApi.updateDocument(this.currentDocument.id, {
          title: this.documentTitle.trim()
        })
        this.$emit('documentSaved')
      } catch (error) {
        console.error('Error updating title:', error)
      }
    }
  }
}
</script>

<style scoped>
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