<template>
  <div class="app-layout">
    <div v-if="isSidebarOpen" class="sidebar-overlay" @click="isSidebarOpen = false" />
    <AppSidebar v-if="isAuthInitialized" :is-open="isSidebarOpen" @close="isSidebarOpen = false" />
    <main class="page-content">
      <div v-if="isAuthInitialized" class="page-header">
        <button class="hamburger-button" aria-label="메뉴 열기" @click="isSidebarOpen = true">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <AppHeaderActions />
      </div>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import AppHeaderActions from './components/AppHeaderActions.vue'
import { useAuth } from './composables/useAuth.js'
import { onMounted } from 'vue'
const { checkAuth, isAuthInitialized } = useAuth()

const isSidebarOpen = ref(false)

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
  min-width: 0;
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.hamburger-button {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  margin-right: auto;
  padding: 6px;
  border: none;
  background: none;
  cursor: pointer;
}

.hamburger-button span {
  display: block;
  width: 22px;
  height: 2px;
  border-radius: 2px;
  background-color: var(--color-text);
  transition: background-color 0.15s;
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .hamburger-button {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 99;
    background-color: rgb(0 0 0 / 40%);
  }
}
</style>
