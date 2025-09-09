<template>
  <div class="app">
    <!-- 左侧文件列表 -->
    <div class="left-panel">
      <div class="panel-header">
        <h3>文件列表</h3>
        <div class="header-buttons">
          <button @click="refreshFileList" class="refresh-btn" title="刷新文件列表">刷新文件列表</button>
          <button @click="addNewFile" class="add-btn">+ 新建</button>
        </div>
      </div>
      <div class="file-list">
        <div 
          v-for="file in files" 
          :key="file.id"
          :class="['file-item', { active: currentFileId === file.id }]"
          @click="selectFile(file.id)"
        >
          <span class="file-name">{{ file.title }}</span>
        </div>
      </div>
    </div>

    <!-- 中间Monaco编辑器 -->
    <div class="center-panel" style="padding-top: 10px; padding-bottom: 10px;">
      <div class="editor-container">
        <div ref="monacoEditor" class="monaco-editor"></div>
      </div>
    </div>

    <!-- 右侧操作面板 -->
    <div class="right-panel">
      <div class="panel-header">
        <h3>操作</h3>
        <button @click="refreshCurrentFile" class="refresh-btn" title="刷新当前文件">刷新当前文件</button>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button @click="saveFile" class="action-btn save-btn">保存</button>
        <button @click="runCode" class="action-btn run-btn">运行</button>
      </div>

      <!-- 输出结果区域 -->
      <div class="output-section">
        <div class="panel-header">
          <h3>输出结果</h3>
          <button @click="clearOutput" class="clear-btn">清空</button>
        </div>
        <div class="output-container">
          <pre class="output-content">{{ output }}</pre>
        </div>
      </div>
    </div>

    <!-- 文件名输入弹窗 -->
    <div v-if="showFileNameDialog" class="modal-overlay" @click="closeFileNameDialog">
      <div class="modal-content" @click.stop>
        <h3>创建新文件</h3>
        <div class="input-group">
          <label for="fileName">文件名:</label>
          <input 
            id="fileName"
            v-model="newFileName" 
            type="text" 
            placeholder="请输入文件名"
            @keyup.enter="confirmCreateFile"
            ref="fileNameInput"
          />
          <span class="file-extension">.lix</span>
        </div>
        <div class="modal-buttons">
          <button @click="closeFileNameDialog" class="cancel-btn">取消</button>
          <button @click="confirmCreateFile" class="confirm-btn">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import * as monaco from 'monaco-editor'

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// 响应式数据
const files = ref([])
const currentFileId = ref(null)
const output = ref('')
const monacoEditor = ref(null)
let editor = null

// 文件名弹窗相关
const showFileNameDialog = ref(false)
const newFileName = ref('')
const fileNameInput = ref(null)

// 获取当前文件
const currentFile = computed(() => {
  return files.value.find(file => file.id === currentFileId.value)
})

// API调用函数
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API调用失败:', error)
    output.value += `\n[${new Date().toLocaleTimeString()}] API错误: ${error.message}\n`
    throw error
  }
}

// 加载所有文档
const loadDocuments = async () => {
  try {
    const documents = await apiCall('/documents')
    files.value = documents
    if (documents.length > 0 && !currentFileId.value) {
      currentFileId.value = documents[0].id
    }
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

// 创建新文档
const createDocument = async (title, content = '') => {
  try {
    const newDoc = await apiCall('/documents', {
      method: 'POST',
      body: JSON.stringify({ title, content })
    })
    files.value.push(newDoc)
    return newDoc
  } catch (error) {
    console.error('创建文档失败:', error)
    return null
  }
}

// 更新文档
const updateDocument = async (id, updates) => {
  try {
    const updatedDoc = await apiCall(`/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    })
    
    const index = files.value.findIndex(f => f.id === id)
    if (index !== -1) {
      files.value[index] = updatedDoc
    }
    return updatedDoc
  } catch (error) {
    console.error('更新文档失败:', error)
    return null
  }
}

// 选择文件
const selectFile = (fileId) => {
  currentFileId.value = fileId
  if (editor && currentFile.value) {
    editor.setValue(currentFile.value.content)
  }
}

// 刷新文件列表
const refreshFileList = async () => {
  try {
    await loadDocuments()
    output.value += `\n[${new Date().toLocaleTimeString()}] 文件列表已刷新\n`
  } catch (error) {
    console.error('刷新文件列表失败:', error)
  }
}

// 刷新当前文件
const refreshCurrentFile = async () => {
  if (currentFile.value) {
    try {
      const updatedDoc = await apiCall(`/documents/${currentFile.value.id}`)
      const index = files.value.findIndex(f => f.id === currentFile.value.id)
      if (index !== -1) {
        files.value[index] = updatedDoc
        if (editor) {
          editor.setValue(updatedDoc.content)
        }
      }
      output.value += `\n[${new Date().toLocaleTimeString()}] 文件已刷新: ${currentFile.value.title}\n`
    } catch (error) {
      console.error('刷新文件失败:', error)
    }
  }
}

// 打开文件名输入弹窗
const addNewFile = () => {
  newFileName.value = ''
  showFileNameDialog.value = true
  nextTick(() => {
    if (fileNameInput.value) {
      fileNameInput.value.focus()
    }
  })
}

// 关闭文件名输入弹窗
const closeFileNameDialog = () => {
  showFileNameDialog.value = false
  newFileName.value = ''
}

// 确认创建文件
const confirmCreateFile = async () => {
  if (!newFileName.value.trim()) {
    alert('请输入文件名')
    return
  }
  
  const fileName = newFileName.value.trim()
  const fullFileName = fileName.endsWith('.lix') ? fileName : `${fileName}.lix`
  
  const newFile = await createDocument(fullFileName, '# Here to write your code')
  if (newFile) {
    selectFile(newFile.id)
    closeFileNameDialog()
  }
}

// 保存文件
const saveFile = async () => {
  if (editor && currentFile.value) {
    const content = editor.getValue()
    const title = currentFile.value.title
    
    const updatedDoc = await updateDocument(currentFile.value.id, {
      title,
      content
    })
    
    if (updatedDoc) {
      console.log('文件已保存:', title)
      output.value += `\n[${new Date().toLocaleTimeString()}] 文件已保存: ${title}\n`
    }
  }
}

const runLitex = async (code) => {
    try {
        const response = await fetch("https://litexlang.org/api/litex", {
            "method": "POST",
            "body": JSON.stringify({
                "targetFormat": "Run Litex",
                "litexString": code
            })
        })
        if (!response.ok) {
            return "Network Error: " + response.statusText
        }
        const data = await response.json()
        return data.data
    } catch (error) {
        return "Error: " + error.message
    }
}

// 运行代码 - 留给你自己实现
const runCode = async () => {
  if (editor && currentFile.value) {
    const content = editor.getValue()
    // console.log('运行代码:', content)
    const response = await runLitex(content)
    
    // 这里留给你自己实现运行逻辑
    // 你可以调用后端API或者在前端执行代码
    output.value += `\n[${new Date().toLocaleTimeString()}] 运行 ${currentFile.value.title}:\n${response}\n`
  }
}

// 清空输出
const clearOutput = () => {
  output.value = ''
}

// 初始化Monaco编辑器
const initMonaco = async () => {
  await nextTick()
  
  if (monacoEditor.value) {
    editor = monaco.editor.create(monacoEditor.value, {
      value: currentFile.value?.content || '',
      theme: 'vs-dark',
      automaticLayout: true,
      fontSize: 14,
      minimap: { enabled: false },
      scrollBeyondLastLine: false
    })

    // 监听内容变化
    editor.onDidChangeModelContent(() => {
      // 可以在这里添加自动保存逻辑
    })
  }
}

// 监听文件变化，更新编辑器内容
watch(currentFileId, () => {
  if (editor && currentFile.value) {
    editor.setValue(currentFile.value.content)
  }
})

// 组件挂载后初始化
onMounted(async () => {
  await loadDocuments()
  await initMonaco()
})
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  background-color: #1e1e1e;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 左侧面板 */
.left-panel {
  width: 250px;
  background-color: #252526;
  border-right: 1px solid #3e3e42;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #3e3e42;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.header-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.add-btn {
  background-color: #0e639c;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.add-btn:hover {
  background-color: #1177bb;
}

.refresh-btn {
  background-color: #0e639c;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.refresh-btn:hover {
  background-color: #1177bb;
}

.file-list {
  flex: 1;
  overflow-y: auto;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  cursor: pointer;
  border-bottom: 1px solid #2d2d30;
}

.file-item:hover {
  background-color: #2a2d2e;
}

.file-item.active {
  background-color: #37373d;
}

.file-name {
  font-size: 13px;
}

/* 中间面板 */
.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-container {
  flex: 1;
  position: relative;
}

.monaco-editor {
  width: 100%;
  height: 100%;
}

/* 右侧面板 */
.right-panel {
  width: 350px;
  background-color: #252526;
  border-left: 1px solid #3e3e42;
  display: flex;
  flex-direction: column;
}

.action-buttons {
  padding: 15px;
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.save-btn {
  background-color: #0e639c;
  color: white;
}

.save-btn:hover {
  background-color: #1177bb;
}

.run-btn {
  background-color: #28a745;
  color: white;
}

.run-btn:hover {
  background-color: #34ce57;
}

.clear-btn {
  background: none;
  border: none;
  color: #cccccc;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
}

.clear-btn:hover {
  color: #ffffff;
}

.output-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.output-container {
  flex: 1;
  padding: 15px;
  min-height: 200px;
  max-height: 500px;
}

.output-content {
  background-color: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  padding: 10px;
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-y: auto;
  min-height: 200px;
  max-height: 500px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #252526;
  border: 1px solid #3e3e42;
  border-radius: 8px;
  padding: 20px;
  min-width: 300px;
  max-width: 500px;
}

.modal-content h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #cccccc;
}

.input-group input {
  width: 100%;
  padding: 8px 12px;
  background-color: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  box-sizing: border-box;
}

.input-group input:focus {
  outline: none;
  border-color: #0e639c;
}

.file-extension {
  color: #888;
  font-size: 14px;
  margin-left: 8px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.confirm-btn {
  background-color: #0e639c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.confirm-btn:hover {
  background-color: #1177bb;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1e1e1e;
}

::-webkit-scrollbar-thumb {
  background: #3e3e42;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4e4e52;
}
</style>
