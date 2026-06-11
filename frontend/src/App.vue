<template>
  <div class="app-layout">
    <AppSidebar v-if="isAuthInitialized" />
    <main class="page-content">
      <div v-if="isAuthInitialized" class="page-header">
        <AppHeaderActions />
      </div>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppHeaderActions from './components/AppHeaderActions.vue'
import { useAuth } from './composables/useAuth.js'
import { onMounted } from 'vue'
const { checkAuth, isAuthInitialized } = useAuth()

onMounted(() => {
  checkAuth()
})
</script>

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
