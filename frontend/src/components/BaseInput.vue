<template>
  <div class="base-input">
    <label v-if="label" :for="inputId" class="base-input__label">
      {{ label }}
      <span v-if="required" class="base-input__required" aria-hidden="true">*</span>
    </label>

    <input
      v-bind="$attrs"
      :id="inputId"
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :aria-invalid="Boolean(errorMessage)"
      :aria-describedby="descriptionId"
      class="base-input__control"
      :class="{ 'base-input__control--error': errorMessage }"
      @input="$emit('update:modelValue', $event.target.value)"
    />

    <p v-if="errorMessage" :id="errorId" class="base-input__message base-input__message--error">
      {{ errorMessage }}
    </p>
    <p v-else-if="hint" :id="hintId" class="base-input__message">
      {{ hint }}
    </p>
  </div>
</template>

<script setup>
import { computed, useId } from 'vue'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  id: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  placeholder: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  errorMessage: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['update:modelValue'])

const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
const errorId = computed(() => `${inputId.value}-error`)
const hintId = computed(() => `${inputId.value}-hint`)
const descriptionId = computed(() => {
  if (props.errorMessage) {
    return errorId.value
  }

  return props.hint ? hintId.value : undefined
})
</script>

<style scoped>
.base-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.base-input__label {
  color: var(--gray-700);
  font-size: 13px;
  font-weight: 600;
}

.base-input__required {
  color: var(--color-danger);
}

.base-input__control {
  width: 100%;
  min-height: 40px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-surface);
  padding: 0 var(--space-3);
  color: var(--color-text);
  outline: none;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.base-input__control::placeholder {
  color: var(--color-text-tertiary);
}

.base-input__control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(59 130 246 / 10%);
}

.base-input__control--error {
  border-color: var(--color-danger);
}

.base-input__control--error:focus {
  box-shadow: 0 0 0 3px rgb(239 68 68 / 10%);
}

.base-input__control:disabled {
  background-color: var(--gray-100);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.base-input__message {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-caption);
}

.base-input__message--error {
  color: var(--color-danger);
}
</style>
