<template>
  <div class="app-container">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="logo">
        <span class="logo-icon">💾</span>
        <span class="logo-text">DiskCleaner</span>
      </div>
      <nav class="nav-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['nav-tab', { active: currentTab === tab.id }]"
          @click="currentTab = tab.id"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-name">{{ tab.name }}</span>
        </button>
      </nav>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 磁盘体检 -->
      <div v-if="currentTab === 'disk'" class="panel">
        <div class="panel-header">
          <h2>🩺 磁盘体检</h2>
          <button class="btn-refresh" @click="refreshDiskInfo">
            <span v-if="loading.disk">⏳</span>
            <span v-else>🔄</span>
          </button>
        </div>
        <div class="disk-cards">
          <div v-for="disk in diskInfo" :key="disk.device" class="disk-card">
            <div class="disk-header">
              <span class="disk-name">{{ disk.volumeName }}</span>
              <span class="disk-percent" :class="disk.percent > 90 ? 'danger' : disk.percent > 70 ? 'warning' : 'safe'">
                {{ disk.percent }}%
              </span>
            </div>
            <div class="disk-visual">
              <div class="disk-bar">
                <div 
                  class="disk-used" 
                  :style="{ width: disk.percent + '%' }"
                  :class="disk.percent > 90 ? 'danger' : disk.percent > 70 ? 'warning' : 'safe'"
                ></div>
              </div>
            </div>
            <div class="disk-stats">
              <div class="stat">
                <span class="stat-label">已用</span>
                <span class="stat-value">{{ formatSize(disk.used) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">可用</span>
                <span class="stat-value">{{ formatSize(disk.free) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">总容量</span>
                <span class="stat-value">{{ formatSize(disk.total) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 垃圾清理 -->
      <div v-if="currentTab === 'clean'" class="panel">
        <div class="panel-header">
          <h2>🧹 垃圾清理</h2>
          <button class="btn-primary" @click="scanGarbage" :disabled="loading.clean">
            {{ loading.clean ? '扫描中...' : '一键扫描' }}
          </button>
        </div>
        
        <div v-if="!scanResult" class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>点击"一键扫描"开始检测垃圾文件</p>
        </div>
        
        <div v-else class="clean-categories">
          <div v-for="(cat, key) in scanResult.categories" :key="key" class="clean-category">
            <div class="category-header">
              <div class="category-info">
                <span class="category-icon">{{ getCategoryIcon(key) }}</span>
                <span class="category-name">{{ cat.name }}</span>
              </div>
              <div class="category-stats">
                <span class="category-size">{{ formatSize(cat.size) }}</span>
                <span class="category-count">{{ cat.files.length }} 个文件</span>
              </div>
            </div>
            <div class="category-actions">
              <button class="btn-small" @click="cleanCategory(key)">清理</button>
            </div>
          </div>
          
          <div class="clean-summary">
            <div class="summary-item">
              <span class="summary-label">共发现垃圾</span>
              <span class="summary-value">{{ formatSize(scanResult.totalSize) }}</span>
            </div>
            <button class="btn-danger" @click="cleanAll">一键清理全部</button>
          </div>
        </div>
      </div>

      <!-- 程序卸载 -->
      <div v-if="currentTab === 'uninstall'" class="panel">
        <div class="panel-header">
          <h2>📦 程序卸载</h2>
          <div class="search-box">
            <input 
              v-model="searchKeyword" 
              placeholder="搜索程序..." 
              class="search-input"
            />
          </div>
        </div>
        
        <div v-if="loading.programs" class="loading-state">
          <span>⏳ 加载中...</span>
        </div>
        
        <div v-else class="program-list">
          <div 
            v-for="program in filteredPrograms" 
            :key="program.name"
            class="program-item"
          >
            <div class="program-info">
              <span class="program-name">{{ program.name }}</span>
              <span class="program-publisher">{{ program.publisher || '未知发布者' }}</span>
            </div>
            <div class="program-actions">
              <button class="btn-uninstall" @click="uninstallProgram(program)">卸载</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 大文件查找 -->
      <div v-if="currentTab === 'largefile'" class="panel">
        <div class="panel-header">
          <h2>📁 大文件查找</h2>
          <div class="size-filter">
            <label>最小文件大小：</label>
            <select v-model="minFileSize" class="size-select">
              <option value="50">50 MB</option>
              <option value="100">100 MB</option>
              <option value="500">500 MB</option>
              <option value="1000">1 GB</option>
            </select>
          </div>
        </div>
        
        <div v-if="loading.largefile" class="loading-state">
          <span>⏳ 扫描中，请稍候...</span>
        </div>
        
        <div v-else-if="largeFiles.length" class="largefile-list">
          <div 
            v-for="file in largeFiles" 
            :key="file.path"
            class="largefile-item"
          >
            <div class="file-info">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-path">{{ file.folder }}</span>
            </div>
            <div class="file-meta">
              <span class="file-size">{{ file.sizeMB }} MB</span>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">📂</div>
          <p>点击"扫描"查找大文件</p>
          <button class="btn-primary" @click="findLargeFiles" :disabled="loading.largefile">
            开始扫描
          </button>
        </div>
      </div>
    </main>

    <!-- 确认对话框 -->
    <el-dialog v-model="showConfirm" title="确认清理" width="400">
      <p>{{ confirmMessage }}</p>
      <template #footer>
        <button class="btn-secondary" @click="showConfirm = false">取消</button>
        <button class="btn-danger" @click="confirmClean">确认清理</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const tabs = [
  { id: 'disk', name: '磁盘体检', icon: '🩺' },
  { id: 'clean', name: '垃圾清理', icon: '🧹' },
  { id: 'uninstall', name: '程序卸载', icon: '📦' },
  { id: 'largefile', name: '大文件', icon: '📁' }
]

const currentTab = ref('disk')
const loading = ref({
  disk: false,
  clean: false,
  programs: false,
  largefile: false
})

const diskInfo = ref([])
const scanResult = ref(null)
const programs = ref([])
const searchKeyword = ref('')
const minFileSize = ref(100)
const largeFiles = ref([])

const showConfirm = ref(false)
const confirmMessage = ref('')
const pendingClean = ref(null)

const filteredPrograms = computed(() => {
  if (!searchKeyword.value) return programs.value
  const keyword = searchKeyword.value.toLowerCase()
  return programs.value.filter(p => 
    p.name.toLowerCase().includes(keyword)
  )
})

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return bytes.toFixed(1) + ' ' + units[i]
}

function getCategoryIcon(key) {
  const icons = {
    temp: '📄',
    browser_cache: '🌐',
    log: '📋'
  }
  return icons[key] || '📁'
}

async function refreshDiskInfo() {
  loading.value.disk = true
  try {
    const result = await window.electronAPI.getDiskInfo()
    if (result.success) {
      diskInfo.value = result.disks
    } else {
      ElMessage.error('获取磁盘信息失败')
    }
  } catch (e) {
    ElMessage.error('获取磁盘信息失败: ' + e.message)
  }
  loading.value.disk = false
}

async function scanGarbage() {
  loading.value.clean = true
  try {
    const result = await window.electronAPI.scanGarbage()
    if (result.success) {
      scanResult.value = result
      ElMessage.success('扫描完成')
    } else {
      ElMessage.error('扫描失败')
    }
  } catch (e) {
    ElMessage.error('扫描失败: ' + e.message)
  }
  loading.value.clean = false
}

function cleanCategory(key) {
  const cat = scanResult.value.categories[key]
  if (cat.files.length === 0) {
    ElMessage.warning('该类别没有文件需要清理')
    return
  }
  pendingClean.value = { type: 'category', key, files: cat.files }
  confirmMessage.value = `确定要清理"${cat.name}"吗？将删除 ${cat.files.length} 个文件，释放 ${formatSize(cat.size)} 空间`
  showConfirm.value = true
}

function cleanAll() {
  if (!scanResult.value) return
  const allFiles = Object.values(scanResult.value.categories).flatMap(c => c.files)
  if (allFiles.length === 0) {
    ElMessage.warning('没有文件需要清理')
    return
  }
  pendingClean.value = { type: 'all', files: allFiles }
  confirmMessage.value = `确定要清理全部垃圾文件吗？将删除 ${allFiles.length} 个文件，释放 ${formatSize(scanResult.value.totalSize)} 空间`
  showConfirm.value = true
}

async function confirmClean() {
  showConfirm.value = false
  if (!pendingClean.value) return
  
  try {
    const paths = pendingClean.value.files.map(f => f.path)
    const result = await window.electronAPI.cleanGarbage(paths)
    if (result.success) {
      ElMessage.success(`清理完成！已清理 ${result.cleaned} 个文件，释放 ${formatSize(result.size)} 空间`)
      scanGarbage() // 重新扫描
    } else {
      ElMessage.error('清理失败')
    }
  } catch (e) {
    ElMessage.error('清理失败: ' + e.message)
  }
  
  pendingClean.value = null
}

async function loadPrograms() {
  loading.value.programs = true
  try {
    const result = await window.electronAPI.getPrograms()
    if (result.success) {
      programs.value = result.programs
    } else {
      ElMessage.error('获取程序列表失败')
    }
  } catch (e) {
    ElMessage.error('获取程序列表失败: ' + e.message)
  }
  loading.value.programs = false
}

async function uninstallProgram(program) {
  if (!confirm(`确定要卸载"${program.name}"吗？`)) return
  
  try {
    const result = await window.electronAPI.uninstallProgram(program.name)
    if (result.success) {
      ElMessage.success('卸载已开始')
      loadPrograms() // 重新加载
    } else {
      ElMessage.error(result.error || '卸载失败')
    }
  } catch (e) {
    ElMessage.error('卸载失败: ' + e.message)
  }
}

async function findLargeFiles() {
  loading.value.largefile = true
  largeFiles.value = []
  try {
    const result = await window.electronAPI.findLargeFiles(minFileSize.value)
    if (result.success) {
      largeFiles.value = result.files
      ElMessage.success(`找到 ${result.count} 个大文件`)
    } else {
      ElMessage.error('扫描失败')
    }
  } catch (e) {
    ElMessage.error('扫描失败: ' + e.message)
  }
  loading.value.largefile = false
}

onMounted(() => {
  refreshDiskInfo()
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
}

/* 头部 */
.header {
  display: flex;
  align-items: center;
  padding: 16px 32px;
  background: rgba(30, 30, 50, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 48px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-tabs {
  display: flex;
  gap: 8px;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: #a0a0a0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-tab.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  color: #fff;
  border: 1px solid rgba(102, 126, 234, 0.5);
}

.tab-icon {
  font-size: 18px;
}

.tab-name {
  font-size: 14px;
  font-weight: 500;
}

/* 主内容 */
.main-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

.panel {
  max-width: 1000px;
  margin: 0 auto;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.panel-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
}

/* 按钮 */
.btn-primary {
  padding: 12px 24px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-refresh {
  padding: 10px 16px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
}

.btn-danger {
  padding: 12px 24px;
  border: none;
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary {
  padding: 12px 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 10px;
  cursor: pointer;
}

.btn-small {
  padding: 6px 14px;
  border: none;
  background: rgba(102, 126, 234, 0.3);
  color: #fff;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.btn-uninstall {
  padding: 8px 16px;
  border: 1px solid rgba(220, 38, 38, 0.5);
  background: transparent;
  color: #ef4444;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-uninstall:hover {
  background: rgba(220, 38, 38, 0.2);
}

/* 磁盘卡片 */
.disk-cards {
  display: grid;
  gap: 20px;
}

.disk-card {
  background: rgba(30, 30, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
}

.disk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.disk-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.disk-percent {
  font-size: 20px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 8px;
}

.disk-percent.safe {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.disk-percent.warning {
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.disk-percent.danger {
  background: rgba(220, 38, 38, 0.2);
  color: #ef4444;
}

.disk-visual {
  margin-bottom: 16px;
}

.disk-bar {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.disk-used {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.disk-used.safe {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.disk-used.warning {
  background: linear-gradient(90deg, #eab308 0%, #facc15 100%);
}

.disk-used.danger {
  background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
}

.disk-stats {
  display: flex;
  gap: 32px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #a0a0a0;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

/* 垃圾清理 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  color: #a0a0a0;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.clean-categories {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.clean-category {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: rgba(30, 30, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  font-size: 24px;
}

.category-name {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.category-stats {
  display: flex;
  gap: 16px;
  color: #a0a0a0;
  font-size: 14px;
}

.category-size {
  color: #667eea;
  font-weight: 600;
}

.clean-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  margin-top: 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
}

.summary-label {
  color: #a0a0a0;
  margin-right: 12px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

/* 程序列表 */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 60px;
  color: #a0a0a0;
  font-size: 16px;
}

.search-box {
  display: flex;
  align-items: center;
}

.search-input {
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  width: 240px;
}

.search-input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.5);
}

.program-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
}

.program-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(30, 30, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.program-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.program-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.program-publisher {
  font-size: 12px;
  color: #a0a0a0;
}

/* 大文件 */
.size-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #a0a0a0;
}

.size-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  border-radius: 8px;
}

.largefile-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
}

.largefile-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(30, 30, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-path {
  font-size: 12px;
  color: #a0a0a0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  white-space: nowrap;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
