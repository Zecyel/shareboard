<template>
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
</template>

<script>
import { documentApi } from '../services/api'

export default {
  name: 'DocumentList',
  emits: ['documentSelected', 'documentsUpdated'],
  props: {
    selectedDocumentId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      documents: []
    }
  },
  async mounted() {
    await this.loadDocuments()
  },
  methods: {
    async loadDocuments() {
      try {
        const response = await documentApi.getDocuments()
        this.documents = response.data
        this.$emit('documentsUpdated', this.documents)
      } catch (error) {
        console.error('Error loading documents:', error)
      }
    },
    
    async createNewDocument() {
      try {
        const response = await documentApi.createDocument({
          title: 'New Document',
          content: ''
        })
        await this.loadDocuments()
        this.selectDocument(response.data.id)
      } catch (error) {
        console.error('Error creating document:', error)
      }
    },
    
    selectDocument(documentId) {
      this.$emit('documentSelected', documentId)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
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
</style>