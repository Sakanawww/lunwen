<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="visible" class="confirm-backdrop" @click.self="onCancel">
        <div class="confirm-dialog">
          <div class="confirm-icon" :class="`confirm-icon-${type}`">
            <i :class="iconFor(type)"></i>
          </div>
          <div class="confirm-body">
            <h3 class="confirm-title">{{ title }}</h3>
            <p class="confirm-message">{{ message }}</p>
          </div>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="onCancel">{{ cancelText }}</button>
            <button class="btn-confirm" :class="`btn-${type}`" @click="onConfirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  visible: boolean
  title?: string
  message: string
  type?: 'danger' | 'warning' | 'info'
  confirmText?: string
  cancelText?: string
}>(), {
  title: '确认操作',
  type: 'danger',
  confirmText: '确认',
  cancelText: '取消',
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const iconFor = (type: string) => ({
  danger: 'ri-delete-bin-line',
  warning: 'ri-alert-line',
  info: 'ri-information-line',
}[type] || 'ri-alert-line')

const onConfirm = () => emit('confirm')
const onCancel = () => emit('cancel')
</script>

<style lang="scss" scoped>
.confirm-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 9998;
}
.confirm-dialog {
  background: var(--bg-card, #fff); border-radius: 12px;
  max-width: 400px; width: 90%; padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  display: flex; flex-direction: column; gap: 16px;
}
.confirm-icon {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
  &.confirm-icon-danger { background: rgba(239,68,68,0.1); color: #DC2626; }
  &.confirm-icon-warning { background: rgba(245,158,11,0.1); color: #D97706; }
  &.confirm-icon-info { background: rgba(59,130,246,0.1); color: #2563EB; }
}
.confirm-body { display: flex; flex-direction: column; gap: 4px; }
.confirm-title { font-size: 18px; font-weight: 600; margin: 0; color: var(--text-primary, #1E190F); }
.confirm-message { font-size: 14px; color: var(--text-secondary, #666); margin: 0; line-height: 1.6; }
.confirm-actions { display: flex; justify-content: flex-end; gap: 12px; }
.btn-cancel, .btn-confirm {
  padding: 8px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid var(--border, #E5E5E5);
}
.btn-cancel { background: transparent; color: var(--text-secondary, #666); }
.btn-confirm { color: #fff; border: none; }
.btn-danger { background: #DC2626; }
.btn-warning { background: #D97706; }
.btn-info { background: #2563EB; }
.confirm-enter-active, .confirm-leave-active { transition: opacity 0.2s ease; }
.confirm-enter-from, .confirm-leave-to { opacity: 0; }
</style>
