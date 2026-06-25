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
        <button type="button" class="summary-link" @click="goMyVideos">
          {{ summaryStats.myVideos }}
        </button>
        <p>내가 올린 영상</p>
      </article>

      <article class="summary-card">
        <button type="button" class="summary-link" @click="goLikedVideos">
          {{ summaryStats.likedVideos }}
        </button>
        <p>좋아요한 영상</p>
      </article>

      <article class="summary-card">
        <button type="button" class="summary-link" @click="goFavorites">
          {{ summaryStats.bookmarks }}
        </button>
        <p>즐겨찾기 제품</p>
      </article>
    </section>
    <p v-if="summaryErrorMessage" class="summary-error">{{ summaryErrorMessage }}</p>

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
        <button type="button" class="text-button" @click="goMyVideos">전체 보기</button>
      </div>

      <p class="empty-message">아직 등록한 영상 후기가 없습니다.</p>
    </section>

    <section class="settings-list">
      <button type="button" @click="openPasswordForm">비밀번호 변경</button>
      <button type="button">알림 설정</button>
      <button type="button" :disabled="isLoggingOut" @click="handleLogout">
        {{ isLoggingOut ? '로그아웃 중...' : '로그아웃' }}
      </button>
      <button type="button" class="danger">회원 탈퇴</button>
    </section>

    <section v-if="isPasswordFormOpen" class="password-card">
      <div class="section-header">
        <h2>비밀번호 변경</h2>
        <button type="button" class="text-button" @click="closePasswordForm">취소</button>
      </div>

      <form class="password-form" @submit.prevent="handlePasswordChange">
        <label for="current-password">현재 비밀번호</label>
        <input
          id="current-password"
          v-model.trim="passwordForm.currentPassword"
          type="password"
          autocomplete="current-password"
          placeholder="현재 비밀번호"
        />

        <label for="new-password">새 비밀번호</label>
        <input
          id="new-password"
          v-model.trim="passwordForm.newPassword"
          type="password"
          autocomplete="new-password"
          placeholder="8자 이상 입력"
        />

        <label for="confirm-password">새 비밀번호 확인</label>
        <input
          id="confirm-password"
          v-model.trim="passwordForm.confirmPassword"
          type="password"
          autocomplete="new-password"
          placeholder="새 비밀번호 확인"
        />

        <p v-if="passwordErrorMessage" class="form-message error-message">
          {{ passwordErrorMessage }}
        </p>
        <p v-if="passwordSuccessMessage" class="form-message success-message">
          {{ passwordSuccessMessage }}
        </p>

        <button type="submit" class="primary-button" :disabled="isChangingPassword">
          {{ isChangingPassword ? '변경 중...' : '비밀번호 변경 완료' }}
        </button>
      </form>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import defaultProfile from '@/assets/images/default-profile.png'
import { useAuth } from '@/composables/useAuth'
import { changeMyPassword } from '@/services/authApi.js'
import { fetchBookmarks } from '@/services/bookmarkApi.js'
import { fetchLikedVideos, fetchMyVideos } from '@/services/videoApi.js'

const router = useRouter()
const { user, logout } = useAuth()
const isLoggingOut = ref(false)
const isPasswordFormOpen = ref(false)
const isChangingPassword = ref(false)
const passwordErrorMessage = ref('')
const passwordSuccessMessage = ref('')
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const summaryErrorMessage = ref('')
const summaryStats = reactive({
  myVideos: '...',
  likedVideos: '...',
  bookmarks: '...',
})

const VIDEO_PAGE_SIZE = 20

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

const countPaginatedVideos = async (fetcher) => {
  let cursor = null
  let total = 0

  while (true) {
    const videos = await fetcher({ cursor })
    total += videos.length

    if (videos.length < VIDEO_PAGE_SIZE) {
      return total
    }

    cursor = videos.at(-1)?.id

    if (!cursor) {
      return total
    }
  }
}

const loadSummaryStats = async () => {
  summaryErrorMessage.value = ''

  const [myVideosResult, likedVideosResult, bookmarksResult] = await Promise.allSettled([
    countPaginatedVideos(fetchMyVideos),
    countPaginatedVideos(fetchLikedVideos),
    fetchBookmarks(),
  ])

  summaryStats.myVideos = myVideosResult.status === 'fulfilled' ? myVideosResult.value : '-'
  summaryStats.likedVideos = likedVideosResult.status === 'fulfilled' ? likedVideosResult.value : '-'
  summaryStats.bookmarks = bookmarksResult.status === 'fulfilled' ? bookmarksResult.value.length : '-'

  const hasRejectedResult = [myVideosResult, likedVideosResult, bookmarksResult].some(
    (result) => result.status === 'rejected',
  )

  if (hasRejectedResult) {
    summaryErrorMessage.value = '일부 마이페이지 정보를 불러오지 못했습니다.'
  }
}

const goProfileEdit = () => {
  router.push('/profile-edit')
}

const goLivingProfile = () => {
  router.push({ name: 'LivingProfile', query: { mode: 'edit' } })
}

const goMyVideos = () => {
  router.push({ name: 'MyVideos' })
}

const goLikedVideos = () => {
  router.push({ name: 'Liked' })
}

const goFavorites = () => {
  router.push({ name: 'Favorite' })
}

const resetPasswordForm = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const openPasswordForm = () => {
  isPasswordFormOpen.value = true
  passwordErrorMessage.value = ''
  passwordSuccessMessage.value = ''
}

const closePasswordForm = () => {
  isPasswordFormOpen.value = false
  passwordErrorMessage.value = ''
  passwordSuccessMessage.value = ''
  resetPasswordForm()
}

const validatePasswordForm = () => {
  if (!passwordForm.currentPassword) {
    passwordErrorMessage.value = '현재 비밀번호를 입력해주세요.'
    return false
  }

  if (passwordForm.newPassword.length < 8) {
    passwordErrorMessage.value = '새 비밀번호는 8자 이상 입력해주세요.'
    return false
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrorMessage.value = '새 비밀번호와 확인 값이 일치하지 않습니다.'
    return false
  }

  passwordErrorMessage.value = ''
  return true
}

const handlePasswordChange = async () => {
  if (isChangingPassword.value || !validatePasswordForm()) {
    return
  }

  isChangingPassword.value = true
  passwordSuccessMessage.value = ''

  try {
    await changeMyPassword({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    })
    resetPasswordForm()
    passwordSuccessMessage.value = '비밀번호가 변경되었습니다.'
  } catch (error) {
    passwordErrorMessage.value = error.message || '비밀번호를 변경하지 못했습니다.'
  } finally {
    isChangingPassword.value = false
  }
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

onMounted(loadSummaryStats)
</script>

<style scoped>
.mypage {
  max-width: 960px;
  margin: 0 auto;
}

.profile-card,
.living-card,
.my-videos,
.password-card,
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

.summary-link {
  display: block;
  border: none;
  background: none;
  color: inherit;
  padding: 0;
  font-family: inherit;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 8px;
  cursor: pointer;
}

.summary-link:hover,
.summary-link:focus-visible {
  text-decoration: underline;
  text-underline-offset: 4px;
}

.summary-link:focus-visible {
  outline: 2px solid #93c5fd;
  outline-offset: 4px;
  border-radius: 6px;
}

.summary-card p {
  margin: 0;
  color: #6b7280;
}

.summary-error {
  margin: -12px 0 20px;
  color: #ef4444;
  font-size: 14px;
}

.living-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.password-form {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.password-form label {
  font-weight: 700;
}

.password-form input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 13px 14px;
  font-size: 15px;
}

.form-message {
  margin: 4px 0 0;
  font-size: 14px;
}

.error-message {
  color: #ef4444;
}

.success-message {
  color: #059669;
}

.primary-button {
  border: none;
  border-radius: 12px;
  background-color: #2563eb;
  color: white;
  padding: 14px 18px;
  font-weight: 700;
  cursor: pointer;
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
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
