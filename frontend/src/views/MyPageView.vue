<template>
  <section class="mypage">
    <section class="profile-card">
      <img
        class="profile-image"
        :src="defaultProfile"
        alt="프로필 이미지"
      />

      <div class="profile-info">
        <h2>{{ user?.nickname || '사용자 정보 없음' }}</h2>
        <p>{{ user?.email || '이메일 정보 없음' }}</p>
      </div>

      <button type="button" class="text-button" @click="goProfileEdit">프로필 편집</button>
    </section>

    <section class="summary-grid">
      <article class="summary-card">
        <strong>-</strong>
        <p>내가 올린 영상</p>
      </article>

      <article class="summary-card">
        <strong>-</strong>
        <p>좋아요한 영상</p>
      </article>

      <article class="summary-card">
        <strong>-</strong>
        <p>즐겨찾기 제품</p>
      </article>
    </section>

    <section class="living-card">
      <div>
        <h2>내 생활환경</h2>
        <p>{{ livingProfileSummary }}</p>
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
      <button type="button" :disabled="isLoggingOut" @click="handleLogout">
        {{ isLoggingOut ? '로그아웃 중...' : '로그아웃' }}
      </button>
      <button type="button" class="danger">회원 탈퇴</button>
    </section>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import defaultProfile from '@/assets/images/default-profile.png'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, logout } = useAuth()
const isLoggingOut = ref(false)

const housingTypeLabelMap = {
  apartment: '아파트',
  villa: '빌라',
  officetel: '오피스텔',
  detached: '단독주택',
}

const livingProfileSummary = computed(() => {
  const housingType = user.value?.housing_type
  const areaSize = user.value?.area_size

  if (!housingType && !areaSize) {
    return '생활환경 정보가 없습니다.'
  }

  const label = housingTypeLabelMap[housingType] || housingType || '주거 형태 미입력'
  const areaText = areaSize ? `${areaSize}평` : '평수 미입력'
  return `${label} · ${areaText}`
})

const goProfileEdit = () => {
  router.push('/profile-edit')
}

const goLivingProfile = () => {
  router.push('/living-profile')
}

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

.settings-list button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
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
