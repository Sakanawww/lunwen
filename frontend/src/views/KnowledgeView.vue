<template>
  <div class="knowledge-page">
    <div class="page-header">
      <div class="page-title">
        <h1><i class="ri-folder-cloud-line"></i> 知识库管理</h1>
        <p class="page-subtitle">上传课程资料并向量化，供智能答疑 RAG 检索引用</p>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="upload-card">
      <h2 class="section-title"><i class="ri-upload-cloud-2-line"></i> 上传资料</h2>
      
      <form @submit.prevent="handleSubmit" class="upload-form">
        <div class="upload-section">
          <div class="course-row">
            <div class="form-group">
              <label for="courseSelect"><i class="ri-book-open-line"></i> 选择课程</label>
              <DropdownSelect
                v-model="selectedCourseId"
                :options="courseOptions"
                placeholder="选择课程…"
              />
            </div>
          </div>

          <div
            class="upload-area"
            :class="{ dragover: isDragover }"
            @dragenter.prevent="handleDragEnter"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept=".txt,.md,.pdf"
              @change="handleFileChange"
              hidden
            />
            <div class="upload-icon">
              <i class="ri-upload-cloud-2-line"></i>
            </div>
            <p class="upload-text">
              拖拽文件到此处，或 <span class="link">点击选择文件</span>
            </p>
            <p class="upload-hint">
              <span v-if="selectedFile">已选择：{{ selectedFile.name }}</span>
              <span v-else>支持 .txt / .md / .pdf 格式</span>
            </p>
          </div>

          <div class="upload-foot">
            <button type="submit" class="btn btn-primary" :disabled="!selectedFile || isUploading">
              <i v-if="isUploading" class="ri-loader-4-line spin"></i>
              <i v-else class="ri-upload-line"></i>
              {{ isUploading ? '向量化中…' : '上传并向量化' }}
            </button>
          </div>
        </div>
      </form>

      <div v-if="uploadMessage" :class="['msg', uploadSuccess ? 'ok' : 'error']">
        <i :class="uploadSuccess ? 'ri-checkbox-circle-line' : 'ri-error-warning-line'"></i>
        {{ uploadMessage }}
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="doc-list">
      <h3 class="list-title">
        <i class="ri-file-list-3-line"></i>
        已入库文档
        <span class="doc-count">{{ documents.length }} 篇</span>
      </h3>

      <div class="table-wrap">
        <table class="doc-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>知识块数</th>
              <th>上传时间</th>
              <th class="num">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in documents" :key="doc.id">
              <td class="td-mono">{{ doc.id }}</td>
              <td>{{ doc.title }}</td>
              <td><span class="badge">{{ doc.chunk_num }} 块</span></td>
              <td class="td-mono">{{ formatDateTime(doc.created_at) }}</td>
              <td class="num">
                <div class="doc-actions">
                  <button
                    class="action-btn"
                    title="预览"
                    @click="openPreview(doc)"
                  >
                    <i class="ri-eye-line"></i>
                  </button>
                  <button
                    class="action-btn danger"
                    title="删除"
                    @click="deleteDocument(doc)"
                  >
                    <i class="ri-delete-bin-6-line"></i>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="documents.length === 0">
              <td colspan="5" class="empty-state">
                <i class="ri-inbox-archive-line"></i>
                <p>暂无文档，请先上传课程资料</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 文档预览弹窗 -->
    <div
      v-if="showPreviewModal"
      class="modal-mask"
      @click.self="closePreview"
    >
      <div class="modal-box modal-wide" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3 id="previewTitle">文档预览</h3>
          <button type="button" class="modal-x" @click="closePreview">
            <i class="ri-close-line"></i>
          </button>
        </div>
        <div class="preview-meta" v-if="previewDoc">
          {{ previewDoc.title }} · {{ previewDoc.chunk_num }} 个知识块
        </div>
        <div class="preview-body">
          <div v-if="previewLoading" class="preview-loading">
            <i class="ri-loader-4-line spin"></i>
            <span>加载中…</span>
          </div>
          <div v-else-if="previewChunks.length === 0" class="preview-empty">
            <i class="ri-file-search-line"></i>
            <p>该文档没有可预览的内容</p>
          </div>
          <div v-else class="preview-chunks">
            <div
              v-for="(chunk, index) in previewChunks"
              :key="index"
              class="chunk-item"
            >
              <div class="chunk-head">
                <i class="ri-file-text-line"></i>
                <span class="chunk-seq">片段 {{ index + 1 }}</span>
                <span>共 {{ previewChunks.length }} 段</span>
              </div>
              <div class="chunk-content">{{ chunk.content }}</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closePreview">
            <i class="ri-close-line"></i> 关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DropdownSelect from '@/components/form/DropdownSelect.vue'
import { useCourseStore } from '@/stores/course.store'
import { api } from '@/utils/request'

interface Document {
  id: number
  title: string
  chunk_num: number
  created_at: string
}

interface Chunk {
  seq: number
  content: string
}

const courseStore = useCourseStore()

const selectedCourseId = ref<number | null>(null)
const selectedFile = ref<File | null>(null)
const isDragover = ref(false)
const isUploading = ref(false)
const uploadMessage = ref('')
const uploadSuccess = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const documents = ref<Document[]>([])

const showPreviewModal = ref(false)
const previewDoc = ref<Document | null>(null)
const previewLoading = ref(false)
const previewChunks = ref<Chunk[]>([])

const courseOptions = computed(() => {
  return courseStore.courses.map(c => ({ value: c.id, label: c.name }))
})

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const handleDragEnter = () => { isDragover.value = true }
const handleDragOver = () => { isDragover.value = true }
const handleDragLeave = () => { isDragover.value = false }

const handleDrop = (event: DragEvent) => {
  isDragover.value = false
  if (event.dataTransfer?.files.length) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

const handleSubmit = async () => {
  if (!selectedFile.value || !selectedCourseId.value) {
    uploadSuccess.value = false
    uploadMessage.value = '请先选择文件和课程'
    return
  }

  isUploading.value = true
  uploadMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('course_id', String(selectedCourseId.value))

    await api.upload('/api/kb/upload', formData)
    uploadSuccess.value = true
    uploadMessage.value = `上传成功：${selectedFile.value.name}，已加入知识库`
    selectedFile.value = null
    if (fileInputRef.value) fileInputRef.value.value = ''

    await loadDocuments()
  } catch (error) {
    uploadSuccess.value = false
    uploadMessage.value = '上传失败，请稍后重试'
  } finally {
    isUploading.value = false
  }
}

const loadDocuments = async () => {
  if (!selectedCourseId.value) return
  try {
    const data: any = await api.get(`/api/kb/docs/${selectedCourseId.value}`)
    documents.value = (Array.isArray(data) ? data : []).map((d: any) => ({
      id: d.id,
      title: d.title,
      chunk_num: d.chunk_num ?? d.chunkNum ?? 0,
      created_at: d.created_at ?? d.createdAt ?? '',
    }))
  } catch (error) {
    console.error('获取文档列表失败:', error)
    documents.value = []
  }
}

const openPreview = async (doc: Document) => {
  previewDoc.value = doc
  previewLoading.value = true
  showPreviewModal.value = true
  previewChunks.value = []

  try {
    const data: any = await api.get(`/api/kb/doc/${doc.id}/preview`)
    previewChunks.value = (data.chunks || data.segments || []).map((c: any, i: number) => ({
      seq: c.seq ?? i + 1,
      content: c.content || c.text || '',
    }))
  } catch (error) {
    console.error('加载预览失败:', error)
    previewChunks.value = []
  } finally {
    previewLoading.value = false
  }
}

const closePreview = () => {
  showPreviewModal.value = false
  previewDoc.value = null
  previewChunks.value = []
}

const deleteDocument = async (doc: Document) => {
  if (!confirm(`确定要删除文档"${doc.title}"吗？`)) return
  try {
    await api.delete(`/api/kb/doc/${doc.id}`)
    documents.value = documents.value.filter(d => d.id !== doc.id)
    uploadSuccess.value = true
    uploadMessage.value = '文档已删除'
  } catch (error) {
    uploadSuccess.value = false
    uploadMessage.value = '删除失败'
  }
}

const formatDateTime = (dateStr: string) => {
  return dateStr ? dateStr.replace('T', ' ').replace(' ', '\n') : '—'
}

watch(selectedCourseId, () => {
  if (selectedCourseId.value) loadDocuments()
})

onMounted(() => {
  if (courseStore.courses.length > 0) {
    selectedCourseId.value = courseStore.currentCourseId || courseStore.courses[0].id
  }
})
</script>

<style lang="scss" scoped>
.knowledge-page {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-6);
}

// 页面标题
.page-header {
  margin-bottom: var(--space-6);

  .page-title {
    h1 {
      font-size: var(--text-2xl);
      font-weight: var(--font-semibold);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: var(--space-2);
      margin: 0;

      i {
        color: rgb(var(--green));
      }
    }

    .page-subtitle {
      font-size: var(--text-sm);
      color: var(--text-secondary);
      margin: var(--space-2) 0 0 0;
    }
  }
}

// 上传卡片
.upload-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0 0 var(--space-4) 0;

  i {
    color: rgb(var(--green));
  }
}

.upload-form {
  .upload-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .course-row {
    display: flex;
    align-items: flex-end;
    gap: var(--space-4);
    flex-wrap: wrap;

    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--space-2);

      label {
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--text-primary);
        margin: 0;
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);

        i {
          color: rgb(var(--green));
        }
      }

      :deep(.dropdown-select) {
        min-width: 220px;
      }
    }
  }
}

.upload-area {
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-8) var(--space-6);
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-input);

  &:hover,
  &.dragover {
    border-color: rgb(var(--green));
    background: rgba(var(--green), 0.05);
  }

  .upload-icon {
    width: 56px;
    height: 56px;
    margin: 0 auto var(--space-3);
    border-radius: var(--radius-lg);
    background: linear-gradient(135deg, rgb(var(--green)), rgb(52, 211, 153));
    display: grid;
    place-items: center;
    color: white;
    font-size: 26px;
    box-shadow: var(--shadow-md);
  }

  .upload-text {
    font-size: var(--text-base);
    color: var(--text-secondary);
    margin: var(--space-2) 0 var(--space-1);

    .link {
      color: rgb(var(--green));
      font-weight: var(--font-medium);
      cursor: pointer;
    }
  }

  .upload-hint {
    font-size: var(--text-sm);
    color: var(--text-muted);
  }
}

.upload-foot {
  display: flex;
  justify-content: center;
  margin-top: var(--space-4);

  .btn {
    min-width: 160px;
  }
}

.msg {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  margin-top: var(--space-4);

  &.ok {
    background: rgba(16, 185, 129, 0.1);
    color: rgb(6, 118, 71);
  }

  &.error {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(185, 28, 28);
  }
}

// 文档列表
.doc-list {
  .list-title {
    font-size: var(--text-lg);
    font-weight: var(--font-medium);
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin: 0 0 var(--space-4) 0;

    i {
      color: rgb(var(--green));
    }

    .doc-count {
      font-size: var(--text-sm);
      font-weight: var(--font-normal);
      color: var(--text-secondary);
      background: rgba(var(--green), 0.1);
      padding: var(--space-1) var(--space-3);
      border-radius: var(--radius-full);
    }
  }
}

.table-wrap {
  overflow-x: auto;
}

.doc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

  thead th {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: var(--font-semibold);
    font-size: var(--text-xs);
    padding: var(--space-3) var(--space-4);
    text-align: left;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }

  tbody {
    td {
      padding: var(--space-3) var(--space-4);
      border-bottom: 1px solid var(--border);
      color: var(--text-secondary);

      &.num {
        text-align: right;
      }
    }

    tr:hover {
      background: var(--bg-tertiary);
    }
  }
}

.td-mono {
  font-family: var(--font-mono);
  white-space: nowrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  background: rgba(var(--green), 0.1);
  color: rgb(var(--green));
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.doc-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.action-btn {
  min-height: 36px;
  min-width: 36px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-lg);

  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-color: rgb(var(--green));
  }

  &.danger:hover {
    background: rgba(239, 68, 68, 0.1);
    color: rgb(239, 68, 68);
    border-color: rgba(239, 68, 68, 0.3);
  }
}

.empty-state {
  text-align: center;
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 48px;
    display: block;
    margin-bottom: var(--space-2);
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}

// 预览弹窗
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5);
}

.modal-box {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.25);
  padding: var(--space-5);
  overflow: hidden;

  &.modal-wide {
    max-width: 760px;
  }
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);

  h3 {
    margin: 0;
    font-size: var(--text-lg);
    color: var(--text-primary);
  }
}

.modal-x {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  line-height: 1;

  &:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
  }
}

.preview-meta {
  display: flex;
  gap: var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-muted);
  padding: var(--space-2) var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.preview-body {
  max-height: 62vh;
  overflow-y: auto;
  padding: var(--space-4);
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-10) 0;
  color: var(--text-secondary);

  .spin {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-10) 0;
  color: var(--text-muted);

  i {
    font-size: 48px;
  }

  p {
    margin: 0;
    font-size: var(--text-sm);
  }
}

.preview-chunks {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.chunk-item {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  overflow: hidden;
}

.chunk-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border);
  font-size: var(--text-xs);
  color: var(--text-secondary);

  i {
    color: rgb(var(--green));
  }

  .chunk-seq {
    font-weight: var(--font-semibold);
    color: var(--text-primary);
  }
}

.chunk-content {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

// 工具类
.spin {
  animation: spin 1s linear infinite;
}
</style>
