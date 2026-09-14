<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast-item"
        :class="`toast-${t.type}`"
        @click="remove(t.id)"
      >
        <i :class="iconFor(t.type)"></i>
        <span>{{ t.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

const iconFor = (type: string) => ({
  success: 'ri-checkbox-circle-line',
  error: 'ri-error-warning-line',
  info: 'ri-information-line',
}[type] || 'ri-information-line')
</script>

<style lang="scss" scoped>
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}
.toast-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: auto;
  max-width: 360px;
  i { font-size: 18px; flex-shrink: 0; }
}
.toast-success { background: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7; }
.toast-error { background: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; }
.toast-info { background: #EFF6FF; color: #1E40AF; border: 1px solid #93C5FD; }
.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-enter-from { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }
</style>
