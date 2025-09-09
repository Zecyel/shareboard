<template>
  <div id="app">
    <div class="app-layout">
      <DocumentList
        :selectedDocumentId="selectedDocumentId"
        @documentSelected="onDocumentSelected"
        @documentsUpdated="onDocumentsUpdated"
        ref="documentList"
      />
      <MonacoEditor
        :documentId="selectedDocumentId"
        @documentSaved="onDocumentSaved"
      />
    </div>
  </div>
</template>

<script>
import DocumentList from './components/DocumentList.vue'
import MonacoEditor from './components/MonacoEditor.vue'

export default {
  name: 'App',
  components: {
    DocumentList,
    MonacoEditor
  },
  data() {
    return {
      selectedDocumentId: null
    }
  },
  methods: {
    onDocumentSelected(documentId) {
      this.selectedDocumentId = documentId
    },
    
    onDocumentsUpdated(documents) {
      // Refresh document list if needed
    },
    
    onDocumentSaved() {
      // Refresh document list to show updated timestamps
      if (this.$refs.documentList) {
        this.$refs.documentList.loadDocuments()
      }
    }
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
</style>