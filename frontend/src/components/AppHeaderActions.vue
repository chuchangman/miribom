<script setup>
import { RouterLink } from 'vue-router'
import { ref } from 'vue'

const isLogin = ref(true)
const logout = () => {
  alert('로그아웃 되었습니다.')
}
</script>

<template>
  <nav>
    <div class="login-actions" v-if="isLogin">
      <button type="button" @click="logout">로그아웃</button>
      <RouterLink to="/mypage">마이페이지</RouterLink>
    </div>
    <div class="guest-actions" v-else>
      <RouterLink to="/login">로그인</RouterLink>
      <RouterLink to="/signup">회원가입</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.login-actions,
.guest-actions {
  display: flex;
  gap: 16px;
  justify-content: end;
}
.login-actions a,
.guest-actions a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
}
.login-actions button {
  background-color: white;
  border: 0;
  color: #333;
  font-weight: 500;
  cursor: pointer;
}
</style>
