<template>
  <div class="category-card" @click="goSearchCategory">
    <CategoryIcon :category="props.category" />
    <h3>{{ props.category.name }}</h3>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import CategoryIcon from '@/components/CategoryIcon.vue'

const props = defineProps({
  category: {
    type: Object,
    required: true,
  },
})

const router = useRouter()

function goSearchCategory() {
  router.push({ name: 'ProductSearch', query: { category: props.category.id } })
}
</script>

<style scoped>
.category-card {
  width: 200px;
  min-height: 124px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 18px;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  background-color: #fff;
  padding: 22px 16px;
  color: var(--color-text);
  text-align: center;
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.category-card h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 0.95rem;
  font-weight: 800;
}

.category-card:hover {
  border-color: var(--category-border);
  box-shadow: 0 14px 30px rgb(15 23 42 / 8%);
  transform: translateY(-2px);
}

.category-card:hover :deep(.category-icon-box) {
  background-color: var(--category-hover-bg);
  color: #fff;
  transform: scale(1.04);
}
</style>
