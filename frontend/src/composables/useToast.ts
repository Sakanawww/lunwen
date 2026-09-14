import { ref } from 'vue'

export interface ToastItem {
  id: number
  type: 'success' | 'error' | 'info'
  message: string
}

const toasts = ref<ToastItem[]>([])
let nextId = 0

function remove(id: number) {
  const idx = toasts.value.findIndex(t => t.id === id)
  if (idx >= 0) toasts.value.splice(idx, 1)
}

function show(type: ToastItem['type'], message: string, duration = 3000) {
  const id = ++nextId
  toasts.value.push({ id, type, message })
  if (duration > 0) setTimeout(() => remove(id), duration)
}

export function useToast() {
  return {
    toasts,
    success: (msg: string) => show('success', msg),
    error: (msg: string) => show('error', msg, 4000),
    info: (msg: string) => show('info', msg),
    remove,
  }
}
