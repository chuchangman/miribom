<template>
  <nav>
    <div v-if="isLogin" class="login-actions">
      <button type="button" :disabled="isLoggingOut" @click="handleLogout">
        {{ isLoggingOut ? '로그아웃 중...' : '로그아웃' }}
      </button>
      <RouterLink to="/mypage">마이페이지</RouterLink>
    </div>
    <div v-else class="guest-actions">
      <RouterLink to="/login">로그인</RouterLink>
      <RouterLink to="/signup">회원가입</RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isLogin, logout } = useAuth()
const isLoggingOut = ref(false)

const handleLogout = async () => {
  if (isLoggingOut.value) {
    return
  }

  isLoggingOut.value = true

  try {
    const isLoggedOut = await logout()

    if (!isLoggedOut) {
      alert('로그아웃에 실패했습니다. 다시 시도해주세요.')
      return
    }

    router.push('/login')
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<style scoped>
.login-actions,
.guest-actions {
  display: flex;
  gap: 16px;
  justify-content: end;
}

.login-actions a,
.guest-actions a {
  color: #333;
  font-weight: 500;
  text-decoration: none;
}

.login-actions button {
  border: 0;
  background-color: transparent;
  color: #333;
  font: inherit;
  font-weight: 500;
  cursor: pointer;
}

.login-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
