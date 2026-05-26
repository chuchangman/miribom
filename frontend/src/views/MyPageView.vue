<script setup>
import { useRouter } from 'vue-router'
import defaultProfile from '@/assets/images/default-profile.png'

const router = useRouter()

const mockUser = {
  nickname: '미리봄 사용자',
  email: 'user@example.com',
  profileImageUrl: '',
  housingType: '원룸',
  areaSize: 7,
  uploadedVideoCount: 0,
  likedVideoCount: 0,
  favoriteProductCount: 4,
}

const goProfileEdit = () => {
  router.push('/profile-edit')
}

const goLivingProfile = () => {
  router.push('/living-profile')
}
</script>

<template>
  <section class="mypage">
    <h1>마이페이지</h1>

    <section class="profile-card">
      <img
        class="profile-image"
        :src="mockUser.profileImageUrl || defaultProfile"
        alt="프로필 이미지"
      />

      <div class="profile-info">
        <h2>{{ mockUser.nickname }}</h2>
        <p>{{ mockUser.email }}</p>
      </div>

      <button type="button" class="text-button" @click="goProfileEdit">프로필 편집</button>
    </section>

    <section class="summary-grid">
      <article class="summary-card">
        <strong>{{ mockUser.uploadedVideoCount }}</strong>
        <p>내가 올린 영상</p>
      </article>

      <article class="summary-card">
        <strong>{{ mockUser.likedVideoCount }}</strong>
        <p>좋아요한 영상</p>
      </article>

      <article class="summary-card">
        <strong>{{ mockUser.favoriteProductCount }}</strong>
        <p>즐겨찾기 제품</p>
      </article>
    </section>

    <section class="living-card">
      <div>
        <h2>내 생활환경</h2>
        <p>{{ mockUser.housingType }} · {{ mockUser.areaSize }}평</p>
        <small>비슷한 공간에서 사용한 전자제품 후기를 우선 확인할 수 있습니다.</small>
      </div>

      <button type="button" class="text-button" @click="goLivingProfile">수정하기</button>
    </section>

    <section class="my-videos">
      <div class="section-header">
        <h2>내가 올린 영상</h2>
        <button type="button" class="text-button">전체 보기</button>
      </div>

      <p class="empty-message">아직 등록한 영상 후기가 없습니다.</p>
    </section>

    <section class="settings-list">
      <button type="button">비밀번호 변경</button>
      <button type="button">알림 설정</button>
      <button type="button">로그아웃</button>
      <button type="button" class="danger">회원 탈퇴</button>
    </section>
  </section>
</template>

<style scoped>
.mypage {
  max-width: 960px;
  margin: 0 auto;
}

.profile-card,
.living-card,
.my-videos,
.settings-list {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background-color: white;
  padding: 20px;
  margin-bottom: 20px;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-image {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  margin: 0 0 4px;
}

.profile-info p {
  margin: 0;
  color: #6b7280;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background-color: white;
  padding: 20px;
}

.summary-card strong {
  display: block;
  font-size: 28px;
  margin-bottom: 8px;
}

.summary-card p {
  margin: 0;
  color: #6b7280;
}

.living-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ecfdf5;
  border-color: #a7f3d0;
}

.living-card h2 {
  margin: 0 0 8px;
}

.living-card p {
  margin: 0 0 4px;
  font-weight: 700;
}

.living-card small {
  color: #059669;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-message {
  color: #6b7280;
}

.settings-list {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.settings-list button {
  padding: 16px 20px;
  border: none;
  border-bottom: 1px solid #e5e7eb;
  background-color: white;
  text-align: left;
  cursor: pointer;
}

.settings-list button:last-child {
  border-bottom: none;
}

.text-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
}

.danger {
  color: #ef4444;
}
</style>
