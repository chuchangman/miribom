<template>
  <span class="category-icon-box" :class="`category-icon-box--${variant}`" :style="categoryStyle">
    <svg
      class="category-icon"
      :class="{ 'category-icon--filled': categoryMeta.icon === 'vacuum' }"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <template v-if="categoryMeta.icon === 'washing-machine'">
        <path d="M3 6h3" />
        <path d="M17 6h.01" />
        <rect width="18" height="20" x="3" y="2" rx="2" />
        <circle cx="12" cy="13" r="5" />
        <path d="M12 18a2.5 2.5 0 0 0 0-5 2.5 2.5 0 0 1 0-5" />
      </template>
      <template v-else-if="categoryMeta.icon === 'refrigerator'">
        <path d="M5 6a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6Z" />
        <path d="M5 10h14" />
        <path d="M15 7v6" />
      </template>
      <template v-else-if="categoryMeta.icon === 'microwave'">
        <rect width="20" height="15" x="2" y="4" rx="2" />
        <rect width="8" height="7" x="6" y="8" rx="1" />
        <path d="M18 8v7" />
        <path d="M6 19v2" />
        <path d="M18 19v2" />
      </template>
      <template v-else-if="categoryMeta.icon === 'vacuum'">
        <path d="M20.66 20 13.87 3.81C13.5 2.97 12.93 2.29 12.16 1.77 11.4 1.26 10.55 1 9.61 1 8.77 1 8 1.21 7.3 1.63S6.04 2.62 5.63 3.32 5 4.8 5 5.64L5.03 9H2.03V14.45C2.65 14.17 3.31 14.03 4 14.03V11.03H9C9.57 11.03 10.04 11.23 10.43 11.62 10.82 12 11 12.47 11 13V20.03H8.91C8.76 20.75 8.44 21.41 7.97 22H13V13C13 12.28 12.8 11.62 12.45 11S11.61 9.91 11 9.56C10.42 9.2 9.75 9 9 9H7V5.64C7 4.92 7.25 4.31 7.76 3.79S8.89 3 9.61 3C10.14 3 10.63 3.16 11.06 3.46S11.81 4.14 12 4.61L18.46 20 16 20.03V22H23V20.03L20.66 20M4 18C4.55 18 5 18.45 5 19S4.55 20 4 20 3 19.55 3 19 3.45 18 4 18M4 16C2.34 16 1 17.34 1 19S2.34 22 4 22 7 20.66 7 19 5.66 16 4 16Z" />
      </template>
      <template v-else-if="categoryMeta.icon === 'sun'">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2" />
        <path d="M12 20v2" />
        <path d="m4.93 4.93 1.41 1.41" />
        <path d="m17.66 17.66 1.41 1.41" />
        <path d="M2 12h2" />
        <path d="M20 12h2" />
        <path d="m6.34 17.66-1.41 1.41" />
        <path d="m19.07 4.93-1.41 1.41" />
      </template>
      <template v-else-if="categoryMeta.icon === 'droplet'">
        <path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z" />
      </template>
      <template v-else-if="categoryMeta.icon === 'monitor'">
        <rect width="20" height="14" x="2" y="3" rx="2" />
        <line x1="8" x2="16" y1="21" y2="21" />
        <line x1="12" x2="12" y1="17" y2="21" />
      </template>
      <template v-else>
        <path d="M5 7 3 5" />
        <path d="M9 6V3" />
        <path d="m13 7 2-2" />
        <circle cx="9" cy="13" r="3" />
        <path d="M11.83 12H20a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h2.17" />
        <path d="M16 16h2" />
      </template>
    </svg>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  category: {
    type: Object,
    required: true,
  },
  variant: {
    type: String,
    default: 'card',
    validator: (value) => ['card', 'sidebar'].includes(value),
  },
})

const categoryMetaMap = {
  'washer-dryer': {
    icon: 'washing-machine',
    color: '#3b82f6',
    bg: '#eff6ff',
    hoverBg: '#3b82f6',
    border: '#93c5fd',
  },
  refrigerator: {
    icon: 'refrigerator',
    color: '#06b6d4',
    bg: '#ecfeff',
    hoverBg: '#06b6d4',
    border: '#a5f3fc',
  },
  'kitchen-appliance': {
    icon: 'microwave',
    color: '#f59e0b',
    bg: '#fffbeb',
    hoverBg: '#f59e0b',
    border: '#fde68a',
  },
  vacuum: {
    icon: 'vacuum',
    color: '#8b5cf6',
    bg: '#f5f3ff',
    hoverBg: '#8b5cf6',
    border: '#ddd6fe',
  },
  seasonal: {
    icon: 'sun',
    color: '#f97316',
    bg: '#fff7ed',
    hoverBg: '#f97316',
    border: '#fed7aa',
  },
  'dehumidifier-humidifier': {
    icon: 'droplet',
    color: '#14b8a6',
    bg: '#f0fdfa',
    hoverBg: '#14b8a6',
    border: '#99f6e4',
  },
  'pc-peripheral': {
    icon: 'monitor',
    color: '#6366f1',
    bg: '#eef2ff',
    hoverBg: '#6366f1',
    border: '#c7d2fe',
  },
  projector: {
    icon: 'projector',
    color: '#ec4899',
    bg: '#fdf2f8',
    hoverBg: '#ec4899',
    border: '#fbcfe8',
  },
}

const categoryMeta = computed(
  () =>
    categoryMetaMap[props.category.slug] || {
      icon: 'projector',
      color: '#3b82f6',
      bg: '#eff6ff',
      hoverBg: '#3b82f6',
      border: '#bfdbfe',
    },
)

const categoryStyle = computed(() => ({
  '--category-color': categoryMeta.value.color,
  '--category-bg': categoryMeta.value.bg,
  '--category-hover-bg': categoryMeta.value.hoverBg,
  '--category-border': categoryMeta.value.border,
}))
</script>

<style scoped>
.category-icon-box {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: var(--category-bg);
  color: var(--category-color);
  transition:
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.category-icon-box--card {
  width: 50px;
  height: 50px;
  border-radius: 14px;
}

.category-icon-box--sidebar {
  width: 28px;
  height: 28px;
  border-radius: 9px;
}

.category-icon {
  width: 56%;
  height: 56%;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.category-icon--filled {
  fill: currentColor;
  stroke: none;
}
</style>
