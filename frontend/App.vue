<template>
  <div class="app">
    <!-- 左侧文件列表 -->
    <div class="left-panel">
      <div class="panel-header">
        <h3>文件列表</h3>
        <button @click="addNewFile" class="add-btn">+ 新建</button>
      </div>
      <div class="file-list">
        <div 
          v-for="file in files" 
          :key="file.id"
          :class="['file-item', { active: currentFileId === file.id }]"
          @click="selectFile(file.id)"
        >
          <span class="file-name">{{ file.name }}</span>
          <button @click.stop="deleteFile(file.id)" class="delete-btn">×</button>
        </div>
      </div>
    </div>

    <!-- 中间Monaco编辑器 -->
    <div class="center-panel">
      <div class="editor-container">
        <div ref="monacoEditor" class="monaco-editor"></div>
      </div>
    </div>

    <!-- 右侧操作面板 -->
    <div class="right-panel">
      <div class="panel-header">
        <h3>操作</h3>
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
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import * as monaco from 'monaco-editor'

// 响应式数据
const files = ref([
  { id: 1, name: 'main.py', content: 'print("Hello, World!")' },
  { id: 2, name: 'script.js', content: 'console.log("Hello from JavaScript!");' }
])
const currentFileId = ref(1)
const output = ref('')
const monacoEditor = ref(null)
let editor = null

// 获取当前文件
const currentFile = computed(() => {
  return files.value.find(file => file.id === currentFileId.value)
})

// 选择文件
const selectFile = (fileId) => {
  currentFileId.value = fileId
  if (editor) {
    editor.setValue(currentFile.value.content)
  }
}

// 添加新文件
const addNewFile = () => {
  const newId = Math.max(...files.value.map(f => f.id)) + 1
  const newFile = {
    id: newId,
    name: `file${newId}.py`,
    content: '# 新文件\nprint("Hello!")'
  }
  files.value.push(newFile)
  selectFile(newId)
}

// 删除文件
const deleteFile = (fileId) => {
  if (files.value.length <= 1) {
    alert('至少需要保留一个文件')
    return
  }
  
  const index = files.value.findIndex(f => f.id === fileId)
  files.value.splice(index, 1)
  
  if (currentFileId.value === fileId) {
    currentFileId.value = files.value[0].id
  }
}

// 保存文件
const saveFile = () => {
  if (editor && currentFile.value) {
    const content = editor.getValue()
    currentFile.value.content = content
    console.log('文件已保存:', currentFile.value.name)
    // 这里可以添加实际的保存逻辑，比如发送到后端
  }
}

// 运行代码 - 留给你自己实现
const runCode = () => {
  if (editor && currentFile.value) {
    const content = editor.getValue()
    console.log('运行代码:', content)
    
    // 这里留给你自己实现运行逻辑
    // 你可以调用后端API或者在前端执行代码
    output.value += `\n[${new Date().toLocaleTimeString()}] 运行 ${currentFile.value.name}:\n${content}\n`
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
      language: 'python',
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
onMounted(() => {
  initMonaco()
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

.delete-btn {
  background: none;
  border: none;
  color: #cccccc;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  color: #ff6b6b;
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
  width: 300px;
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
  overflow-y: auto;
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
  min-height: 200px;
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
