<template>
  <component
    :is="as"
    class="base-card"
    :class="[
      `base-card--${padding}`,
      {
        'base-card--interactive': interactive,
        'base-card--elevated': elevated,
      },
    ]"
  >
    <slot />
  </component>
</template>

<script setup>
defineProps({
  as: {
    type: String,
    default: 'div',
  },
  padding: {
    type: String,
    default: 'normal',
    validator: (value) => ['none', 'compact', 'normal'].includes(value),
  },
  interactive: {
    type: Boolean,
    default: false,
  },
  elevated: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.base-card {
  border: 1px solid var(--gray-100);
  border-radius: var(--radius-xl);
  background-color: var(--color-surface);
}

.base-card--none {
  overflow: hidden;
  padding: 0;
}

.base-card--compact {
  padding: var(--space-3);
}

.base-card--normal {
  padding: var(--space-5);
}

.base-card--elevated {
  box-shadow: var(--shadow-md);
}

.base-card--interactive {
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.base-card--interactive:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
</style>
