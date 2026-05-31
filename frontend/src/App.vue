<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppHeaderActions from './components/AppHeaderActions.vue'
</script>

<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="page-content">
      <div class="page-header">
        <AppHeaderActions />
      </div>
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
.page-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}
</style>
