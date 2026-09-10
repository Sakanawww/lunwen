<template>
  <div class="dropdown-select" :class="{ open: isOpen, disabled }">
    <button
      ref="triggerRef"
      class="dropdown-trigger"
      @click="toggle"
      :disabled="disabled"
      type="button"
    >
      <span v-if="modelValue !== null && modelValue !== undefined" class="selected-label">
        {{ getLabel(modelValue) }}
      </span>
      <span v-else class="placeholder">{{ placeholder }}</span>
      <ChevronDownIcon class="chevron" :class="{ rotated: isOpen }" />
    </button>

    <Teleport to="body">
      <transition name="dropdown-fade">
        <div
          v-if="isOpen"
          ref="popperRef"
          class="dropdown-popper"
          :style="popperStyle"
        >
          <div class="dropdown-options">
            <div
              v-for="option in options"
              :key="option.value"
              class="dropdown-option"
              :class="{ selected: modelValue === option.value, disabled: option.disabled }"
              @click="select(option.value)"
            >
              <span class="option-label">{{ option.label }}</span>
              <CheckIcon v-if="modelValue === option.value" class="check-icon" />
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onClickOutside } from '@vueuse/core'

interface Option {
  value: string | number
  label: string
  disabled?: boolean
}

const props = withDefaults(defineProps<{
  modelValue: string | number | null
  options: Option[]
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: '请选择'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const isOpen = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const popperRef = ref<HTMLElement | null>(null)
const popperStyle = ref<Record<string, string>>({})

const toggle = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      updatePopperPosition()
    }
  }
}

const select = (value: string | number) => {
  emit('update:modelValue', value)
  isOpen.value = false
}

const getLabel = (value: string | number) => {
  return props.options.find(opt => opt.value === value)?.label || ''
}

const updatePopperPosition = () => {
  if (!triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()
  popperStyle.value = {
    top: `${rect.bottom + window.scrollY + 4}px`,
    left: `${rect.left + window.scrollX}px`,
    minWidth: `${rect.width}px`,
    zIndex: '1000'
  }
}

onClickOutside(popperRef, () => {
  isOpen.value = false
})

onMounted(() => {
  window.addEventListener('scroll', updatePopperPosition, true)
  window.addEventListener('resize', updatePopperPosition)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updatePopperPosition, true)
  window.removeEventListener('resize', updatePopperPosition)
})
</script>

<script lang="ts">
// 图标组件 - 使用 SVG 内联
const ChevronDownIcon = {
  template: `
    <svg class="chevron-icon" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const CheckIcon = {
  template: `
    <svg class="check-icon-svg" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M13 4L6 11L3 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}
</script>

<style lang="scss" scoped>
.dropdown-select {
  position: relative;
  display: inline-block;
  width: 100%;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);

  &:hover:not(:disabled) {
    border-color: rgb(var(--green));
    box-shadow: 0 0 0 3px rgba(var(--green), 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: var(--bg-tertiary);
  }

  .chevron {
    width: 16px;
    height: 16px;
    transition: transform 150ms ease;
    
    &.rotated {
      transform: rotate(180deg);
    }
  }
}

.dropdown-popper {
  position: absolute;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 280px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-options {
  padding: var(--space-2);
}

.dropdown-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-base);
  color: var(--text-primary);
  transition: all 0.15s ease;

  &:hover:not(.disabled) {
    background: var(--bg-tertiary);
  }

  &.selected {
    background: rgba(var(--green), 0.1);
    color: rgb(var(--green));
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .option-label {
    flex: 1;
  }

  .check-icon {
    width: 16px;
    height: 16px;
    color: rgb(var(--green));
  }
}

// 过渡动画
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

// 滚动条样式
.dropdown-popper::-webkit-scrollbar {
  width: 6px;
}

.dropdown-popper::-webkit-scrollbar-track {
  background: transparent;
}

.dropdown-popper::-webkit-scrollbar-thumb {
  background: rgba(var(--ink), 0.2);
  border-radius: var(--radius-full);
}

.dropdown-popper::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--ink), 0.3);
}
</style>
