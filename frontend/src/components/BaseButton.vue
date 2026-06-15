<template>
  <button
    :type="type"
    class="base-button"
    :class="[`base-button--${variant}`, `base-button--${size}`, { 'base-button--full': full }]"
    :disabled="disabled || loading"
    :aria-busy="loading"
  >
    <span v-if="loading" class="base-button__spinner" aria-hidden="true"></span>
    <span v-if="loading">{{ loadingLabel }}</span>
    <span v-else><slot /></span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'ghost', 'danger'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  type: {
    type: String,
    default: 'button',
  },
  full: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  loadingLabel: {
    type: String,
    default: '처리 중',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    opacity var(--transition-fast);
}

.base-button--sm {
  min-height: 32px;
  padding: 0 var(--space-3);
  font-size: 13px;
}

.base-button--md {
  min-height: 40px;
  padding: 0 var(--space-4);
  font-size: var(--font-size-body);
}

.base-button--lg {
  min-height: 48px;
  padding: 0 var(--space-5);
  font-size: 15px;
}

.base-button--full {
  width: 100%;
}

.base-button--primary {
  background-color: var(--color-primary);
  color: white;
}

.base-button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.base-button--secondary {
  border-color: var(--color-border);
  background-color: var(--color-surface);
  color: var(--gray-700);
}

.base-button--secondary:hover:not(:disabled) {
  border-color: var(--color-border-strong);
  background-color: var(--gray-50);
}

.base-button--ghost {
  background-color: transparent;
  color: var(--gray-700);
}

.base-button--ghost:hover:not(:disabled) {
  background-color: var(--gray-100);
}

.base-button--danger {
  border-color: var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-danger);
}

.base-button--danger:hover:not(:disabled) {
  border-color: var(--color-danger);
  background-color: var(--color-danger-light);
}

.base-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.base-button__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentcolor;
  border-right-color: transparent;
  border-radius: var(--radius-full);
  animation: button-spin 0.7s linear infinite;
}

@keyframes button-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
