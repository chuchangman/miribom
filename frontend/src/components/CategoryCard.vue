<template>
  <div class="category-card" @click="goSearchCategory">
    <!-- 나중에 아이콘 넣을때 다시 살릴 부분 -->
    <!-- <img src="" :alt="props.category" /> -->
    <h3>{{ props.category }}</h3>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  category: {
    type: String,
    required: true,
  },
})

const router = useRouter()

function goSearchCategory() {
  router.push({ name: 'ProductSearch', query: { category: props.category } })
}
</script>

<style scoped>
.category-card {
  border: 1px solid #ccc;
  padding: 1em;
  width: 200px;
  text-align: center;
  cursor: pointer;
}
.category-card img {
  width: 100%;
  height: auto;
}
</style>
