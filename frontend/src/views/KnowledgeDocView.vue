<template>
  <div class="doc-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.push('/knowledge')"><i class="ri-arrow-left-line"></i> 返回知识库</button>
        <h1>{{ doc?.title || '文档预览' }}</h1>
      </div>
    </div>

    <div v-if="loading" class="loading-state"><i class="ri-loader-4-line spin"></i> 加载中…</div>

    <template v-if="doc && !loading">
      <!-- 文档信息 -->
      <div class="doc-info-card">
        <div class="doc-meta">
          <span><i class="ri-file-text-line"></i> {{ doc.file_name || '—' }}</span>
          <span><i class="ri-stack-line"></i> {{ doc.chunk_num }} 个分块</span>
          <span><i class="ri-time-line"></i> {{ doc.created_at }}</span>
        </div>
        <input class="search-input" v-model="searchQuery" placeholder="搜索分块内容…" />
      </div>

      <!-- 分块内容 -->
      <div class="chunks-list">
        <div
          v-for="(chunk, i) in filteredChunks"
          :key="chunk.seq"
          class="chunk-item"
          :style="{ animationDelay: i * 0.05 + 's' }"
        >
          <div class="chunk-header">
            <span class="chunk-seq">#{{ chunk.seq + 1 }}</span>
          </div>
          <div class="chunk-content" v-html="highlightText(chunk.content)"></div>
        </div>
        <div v-if="filteredChunks.length === 0" class="empty">未找到匹配的分块</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const loading = ref(true)
const doc = ref<any>(null)
const searchQuery = ref('')

const authHeaders = () => ({ 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` })

const filteredChunks = computed(() => {
  const chunks = doc.value?.chunks || []
  if (!searchQuery.value.trim()) return chunks
  const q = searchQuery.value.toLowerCase()
  return chunks.filter((c: any) => c.content?.toLowerCase().includes(q))
})

const highlightText = (text: string) => {
  if (!searchQuery.value.trim()) return text
  const q = searchQuery.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${q})`, 'gi'), '<mark>$1</mark>')
}

const loadDoc = async () => {
  const docId = route.params.docId as string
  loading.value = true
  try {
    const res = await fetch(`/api/kb/doc/${docId}/preview`, { headers: authHeaders() })
    if (res.ok) doc.value = await res.json()
    else toast.error('加载失败')
  } catch { toast.error('网络错误') } finally { loading.value = false }
}

onMounted(() => loadDoc())
</script>

<style lang="scss" scoped>
.doc-detail-page { padding: var(--space-6); max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: var(--space-6); .header-left { display: flex; align-items: center; gap: var(--space-4); } h1 { font-size: var(--text-2xl); font-weight: var(--font-semibold); margin: 0; } }
.back-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--bg-card); cursor: pointer; font-size: var(--text-sm); color: var(--text-secondary); transition: all 0.2s; &:hover { color: var(--text-primary); } }
.loading-state { text-align: center; padding: var(--space-16); color: var(--text-muted); .spin { animation: spin 1s linear infinite; } }
@keyframes spin { to { transform: rotate(360deg); } }
.doc-info-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); margin-bottom: var(--space-6); box-shadow: var(--shadow-sm); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-3); animation: fadeUp 0.4s ease-out both; }
.doc-meta { display: flex; gap: var(--space-5); flex-wrap: wrap; font-size: var(--text-sm); color: var(--text-secondary); span { display: inline-flex; align-items: center; gap: 4px; } }
.search-input { padding: 6px 14px; border: 1px solid var(--border); border-radius: var(--radius-md); font-size: var(--text-sm); width: 240px; background: var(--bg-card); &:focus { outline: none; border-color: rgb(var(--green)); box-shadow: 0 0 0 2px rgba(var(--green),0.1); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.chunks-list { display: flex; flex-direction: column; gap: var(--space-4); }
.chunk-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; animation: fadeUp 0.4s ease-out both; &:hover { box-shadow: var(--shadow-md); } }
.chunk-header { padding: var(--space-2) var(--space-4); background: var(--bg-tertiary); border-bottom: 1px solid var(--border); .chunk-seq { font-size: var(--text-xs); font-weight: 600; color: var(--text-secondary); } }
.chunk-content { padding: var(--space-4) var(--space-6); font-size: var(--text-sm); line-height: 1.8; color: var(--text-primary); white-space: pre-wrap; word-wrap: break-word; mark { background: rgba(var(--green),0.2); color: inherit; padding: 0 2px; border-radius: 2px; } }
.empty { text-align: center; padding: var(--space-16); color: var(--text-muted); }
</style>
