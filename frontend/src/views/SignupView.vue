<template>
  <section class="signup-page">
    <div class="signup-shell">
      <div class="signup-panel">
        <div class="signup-brand">
          <img :src="logoImage" alt="미리봄 로고" class="signup-brand__logo" />
        </div>

        <div class="signup-copy">
          <p>사용 중인 제품과 실제 후기를 더 편하게 기록하고, 맞춤 추천까지 이어서 받아보세요.</p>
        </div>

        <form class="signup-form" @submit.prevent="signup">
          <div class="profile-field">
            <label for="profile-img">프로필 이미지</label>
            <div class="profile-field__body">
              <img :src="previewImageUrl" alt="프로필 이미지 미리보기" class="profile-preview" />
              <label for="profile-img" class="profile-upload-button">이미지 고르기</label>
            </div>
            <input
              id="profile-img"
              type="file"
              accept="image/*"
              name="profile-img"
              @change="handleProfileImgChange"
            />
          </div>

          <div class="field-group">
            <label for="nickname">닉네임</label>
            <input
              id="nickname"
              v-model.trim="nickname"
              type="text"
              placeholder="닉네임"
              @focus="removeNicknameError"
              @blur="validateNickname"
            />
            <p v-if="errorNickname" class="error-message">{{ errorNickname }}</p>
          </div>

          <div class="field-group">
            <label for="email">이메일</label>
            <input
              id="email"
              v-model.trim="email"
              type="email"
              placeholder="email@example.com"
              @focus="removeEmailError"
              @blur="validateEmail"
            />
            <p v-if="errorEmail" class="error-message">{{ errorEmail }}</p>
          </div>

          <div class="field-group">
            <label for="password">비밀번호</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="비밀번호"
              @focus="removePasswordError"
              @blur="validatePassword"
              @input="changePassword"
            />
            <p v-if="errorPassword" class="error-message">{{ errorPassword }}</p>
          </div>

          <div class="field-group">
            <label for="confirm-password">비밀번호 확인</label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              type="password"
              placeholder="비밀번호 확인"
              @focus="removeConfirmPasswordError"
              @blur="checkPasswordMatch"
            />
            <p v-if="errorConfirmPassword" class="error-message">{{ errorConfirmPassword }}</p>
          </div>

          <button id="signup-btn" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? '가입 처리 중...' : '회원가입' }}
          </button>
        </form>

        <RouterLink to="/login" id="login-link">이미 계정이 있으신가요?</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import defaultProfile from '@/assets/images/default-profile.png'
import logoImage from '@/assets/images/miribom-logo.svg'
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { AUTH_API_URL } from '@/config/api'
import { useAuth } from '@/composables/useAuth'

const { login } = useAuth()
const router = useRouter()
const profileImg = ref(null)
const previewImageUrl = ref(defaultProfile)

const nickname = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const errorNickname = ref('')
const errorEmail = ref('')
const errorPassword = ref('')
const errorConfirmPassword = ref('')
const isSubmitting = ref(false)

const handleProfileImgChange = (event) => {
  const file = event.target.files[0]

  if (file) {
    profileImg.value = file
    previewImageUrl.value = URL.createObjectURL(file)
    return
  }

  profileImg.value = null
  previewImageUrl.value = defaultProfile
}

const validateNickname = () => {
  if (nickname.value.length < 3) {
    errorNickname.value = '닉네임은 최소 3자 이상이어야 합니다.'
    return false
  }

  errorNickname.value = ''
  return true
}

const removeNicknameError = () => {
  errorNickname.value = ''
}

const validateEmail = () => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(email.value)) {
    errorEmail.value = '유효한 이메일 주소를 입력해주세요.'
    return false
  }

  errorEmail.value = ''
  return true
}

const removeEmailError = () => {
  errorEmail.value = ''
}

const validatePassword = () => {
  if (password.value.length < 8) {
    errorPassword.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return false
  }

  errorPassword.value = ''
  checkPasswordMatch()
  return true
}

const removePasswordError = () => {
  errorPassword.value = ''
}

const removeConfirmPasswordError = () => {
  errorConfirmPassword.value = ''
}

const checkPasswordMatch = () => {
  if (!confirmPassword.value) {
    errorConfirmPassword.value = '비밀번호 확인을 입력해주세요.'
    return false
  }

  if (password.value !== confirmPassword.value) {
    errorConfirmPassword.value = '비밀번호가 일치하지 않습니다.'
    return false
  }

  errorConfirmPassword.value = ''
  return true
}

const changePassword = () => {
  if (confirmPassword.value) {
    checkPasswordMatch()
  }
}

const signup = async () => {
  if (isSubmitting.value) {
    return
  }

  const validNickname = validateNickname()
  const validEmail = validateEmail()
  const validPassword = validatePassword()
  const passwordsMatch = checkPasswordMatch()

  if (!validNickname || !validEmail || !validPassword || !passwordsMatch) {
    alert('입력한 정보를 확인해주세요.')
    return
  }

  isSubmitting.value = true

  try {
    const response = await fetch(`${AUTH_API_URL}/signup/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        nickname: nickname.value,
        email: email.value,
        password: password.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()

      if (response.status === 400) {
        alert('입력하신 정보를 다시 확인해주세요.')
        return
      }

      if (response.status === 401 || response.status === 409) {
        alert(data.error || '요청 처리에 실패했습니다.')
        return
      }

      alert('요청 처리에 실패했습니다.')
      return
    }

    const isAuthenticated = await login()
    if (!isAuthenticated) {
      alert('회원가입 후 로그인 상태를 확인하지 못했습니다. 다시 로그인해주세요.')
      router.push('/login')
      return
    }

    router.push({ name: 'LivingProfile', query: { mode: 'onboarding' } })
  } catch {
    alert('회원가입 실패')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.signup-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
  padding: 20px 20px 32px;
}

.signup-shell {
  width: min(620px, 100%);
  margin-inline: auto;
}

.signup-panel {
  border: 1px solid var(--color-border);
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgb(59 130 246 / 10%), transparent 34%),
    linear-gradient(180deg, rgb(255 255 255 / 98%), rgb(248 250 252 / 98%));
  padding: clamp(24px, 3vw, 32px);
  box-shadow: var(--shadow-lg);
}

.signup-brand {
  display: grid;
  justify-items: center;
  gap: 8px;
  margin-bottom: 14px;
  text-align: center;
}

.signup-brand__logo {
  width: min(148px, 38vw);
  max-height: 56px;
  height: auto;
}

.signup-brand__description {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
  line-height: 1.5;
}

.signup-copy {
  margin-bottom: 18px;
  text-align: center;
}

.signup-copy h1 {
  margin: 0;
  font-size: clamp(1.9rem, 4vw, 2.5rem);
  line-height: 1.12;
}

.signup-copy p {
  margin: 12px 0 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.signup-form {
  display: grid;
  gap: 14px;
}

.profile-field label,
.field-group label {
  display: block;
  margin-bottom: 10px;
  color: var(--color-text);
  font-size: 1.05rem;
  font-weight: 700;
}

.profile-field__body {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background-color: rgb(255 255 255 / 92%);
}

.profile-preview {
  width: 92px;
  height: 92px;
  border-radius: 50%;
  background-color: #fff;
  object-fit: cover;
  box-shadow: var(--shadow-md);
}

.profile-upload-button {
  width: fit-content;
  margin-left: auto;
  margin-bottom: 0;
  border-radius: 999px;
  background-color: var(--color-primary-light);
  padding: 11px 16px;
  color: var(--color-primary-600);
  cursor: pointer;
}

#profile-img {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.field-group input {
  width: 100%;
  border: 1px solid var(--color-border-strong);
  border-radius: 16px;
  background-color: #fff;
  padding: 14px 16px;
  color: var(--color-text);
  font-size: 1rem;
}

.field-group input::placeholder {
  color: #9ca3af;
}

.field-group input:focus {
  outline: 2px solid rgb(59 130 246 / 18%);
  border-color: var(--color-primary);
}

.error-message {
  margin: 8px 0 0;
  color: var(--color-danger);
  font-size: 0.9rem;
}

#signup-btn {
  width: 100%;
  margin-top: 6px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  padding: 15px 18px;
  color: #fff;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 18px 30px -20px rgb(37 99 235 / 65%);
}

#signup-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

#login-link {
  display: block;
  width: fit-content;
  margin: 24px auto 0;
  color: var(--color-primary-600);
  font-weight: 700;
  text-decoration: none;
}

#login-link:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .signup-page {
    padding-inline: 14px;
  }

  .signup-panel {
    border-radius: 24px;
    padding: 22px 18px;
  }

  .signup-brand__logo {
    width: min(132px, 42vw);
  }

  .profile-field__body {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
