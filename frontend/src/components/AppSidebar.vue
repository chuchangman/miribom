<script setup>
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import miribomLogo from '@/assets/images/miribom-logo.svg'

const { isLogin } = useAuth()
</script>

<template>
  <nav>
    <RouterLink to="/" class="sidebar-logo">
      <img :src="miribomLogo" alt="미리봄 로고" />
    </RouterLink>
    <div class="product-searching">
      <p>탐색</p>
      <RouterLink to="/" class="sidebar-link">홈</RouterLink>
      <RouterLink to="/products" class="sidebar-link">둘러보기</RouterLink>
      <RouterLink to="/shorts" class="sidebar-link">숏폼</RouterLink>
    </div>
    <div class="user-action" v-if="isLogin">
      <p>내 활동</p>
      <RouterLink to="/favorites" class="sidebar-link">즐겨찾기</RouterLink>
      <RouterLink to="/likes" class="sidebar-link">좋아요</RouterLink>
      <RouterLink to="/review" class="sidebar-link">후기 등록</RouterLink>
    </div>
    <div class="category">
      <p>카테고리</p>
      <RouterLink to="/products?category=세탁·건조" class="sidebar-link">세탁·건조</RouterLink>
      <RouterLink to="/products?category=냉장고" class="sidebar-link">냉장고</RouterLink>
      <RouterLink to="/products?category=주방소가전" class="sidebar-link">주방소가전</RouterLink>
      <RouterLink to="/products?category=청소기" class="sidebar-link">청소기</RouterLink>
      <RouterLink to="/products?category=계절가전" class="sidebar-link">계절가전</RouterLink>
      <RouterLink to="/products?category=제습기·가습기" class="sidebar-link"
        >제습기·가습기</RouterLink
      >
      <RouterLink to="/products?category=PC주변기기" class="sidebar-link">PC주변기기</RouterLink>
      <RouterLink to="/products?category=빔프로젝터" class="sidebar-link">빔프로젝터</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
nav {
  width: 150px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f0f0;
  padding: 0.5rem;
  box-sizing: border-box;
}
nav p {
  margin: 16px 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: #777;
}

.sidebar-link {
  display: block;
  padding: 8px 10px;
  margin-bottom: 4px;
  text-decoration: none;
  color: #333;
  border-radius: 6px;
}

.sidebar-link:hover {
  background-color: #e0e0e0;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 0;
}

.sidebar-logo img {
  width: 90px;
  height: auto;
  display: block;
  object-fit: contain;
  border: none;
  padding: 0px;
  margin: 0px;
}
</style>
