<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="page-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.page-content {
  flex: 1;
  padding: 24px;
}
</style>
