<template>
  <section class="login-page">
    <div class="login-shell">
      <div class="login-panel">
        <div class="login-brand">
          <img :src="logoImage" alt="미리봄 로고" class="login-brand__logo" />
          <p class="login-brand__description">실제 사용 영상으로 확인하는 전자제품 후기</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field-group">
            <label for="email">이메일</label>
            <input
              id="email"
              v-model.trim="email"
              type="email"
              placeholder="email@example.com"
              @blur="validateEmail"
              @focus="removeEmailError"
            />
            <p v-if="emailErrorMessage" class="error-message">{{ emailErrorMessage }}</p>
          </div>

          <div class="field-group">
            <div class="field-group__label-row">
              <label for="password">비밀번호</label>
              <button type="button" class="ghost-link" @click="handleForgotPassword">
                비밀번호 찾기
              </button>
            </div>
            <input
              id="password"
              v-model.trim="password"
              type="password"
              placeholder="비밀번호"
              @blur="validatePassword"
              @focus="removePasswordError"
            />
            <p v-if="passwordErrorMessage" class="error-message">{{ passwordErrorMessage }}</p>
          </div>

          <button id="login-btn" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? '로그인 중...' : '로그인' }}
          </button>
        </form>

        <div class="social-divider" aria-hidden="true">
          <span></span>
          <em>또는</em>
          <span></span>
        </div>

        <section class="social-login" aria-label="소셜 로그인">
          <button
            id="kakao-login-btn"
            type="button"
            class="social-login__button social-login__button--kakao"
            @click="oauthLogin('kakao')"
          >
            <span class="social-login__icon social-login__icon--kakao" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false">
                <path
                  d="M12 4C7.03 4 3 7.09 3 10.9c0 2.44 1.65 4.58 4.13 5.79l-.83 3.31c-.07.27.24.49.48.33l3.95-2.62c.42.06.84.09 1.27.09 4.97 0 9-3.09 9-6.9S16.97 4 12 4Z"
                  fill="currentColor"
                />
              </svg>
            </span>
            <span>카카오로 시작하기</span>
          </button>

          <button
            id="google-login-btn"
            type="button"
            class="social-login__button social-login__button--google"
            @click="oauthLogin('google')"
          >
            <span class="social-login__icon social-login__icon--google" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false">
                <path
                  d="M21.64 12.2c0-.64-.06-1.25-.16-1.84H12v3.48h5.41a4.62 4.62 0 0 1-2 3.03v2.52h3.24c1.9-1.75 2.99-4.33 2.99-7.19Z"
                  fill="#4285F4"
                />
                <path
                  d="M12 22c2.7 0 4.96-.89 6.62-2.41l-3.24-2.52c-.9.6-2.06.96-3.38.96-2.6 0-4.8-1.76-5.58-4.12H3.07v2.6A9.99 9.99 0 0 0 12 22Z"
                  fill="#34A853"
                />
                <path
                  d="M6.42 13.91A5.98 5.98 0 0 1 6.1 12c0-.66.11-1.3.32-1.91V7.49H3.07A9.99 9.99 0 0 0 2 12c0 1.61.39 3.13 1.07 4.51l3.35-2.6Z"
                  fill="#FBBC04"
                />
                <path
                  d="M12 5.97c1.47 0 2.8.51 3.84 1.5l2.88-2.88C16.95 2.95 14.69 2 12 2A9.99 9.99 0 0 0 3.07 7.49l3.35 2.6C7.2 7.73 9.4 5.97 12 5.97Z"
                  fill="#EA4335"
                />
              </svg>
            </span>
            <span>구글로 시작하기</span>
          </button>

          <button
            id="naver-login-btn"
            type="button"
            class="social-login__button social-login__button--naver"
            @click="oauthLogin('naver')"
          >
            <span class="social-login__icon social-login__icon--naver" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false">
                <path d="M6 5h4.32l3.36 4.85V5H18v14h-4.32l-3.36-4.85V19H6V5Z" fill="currentColor" />
              </svg>
            </span>
            <span>네이버로 시작하기</span>
          </button>
        </section>

        <RouterLink to="/signup" id="signup-link">계정이 없으신가요?</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import logoImage from '@/assets/images/miribom-logo.svg'
import { AUTH_API_URL } from '@/config/api'
import { useAuth } from '@/composables/useAuth'

const { login } = useAuth()
const router = useRouter()
const email = ref('')
const password = ref('')
const emailErrorMessage = ref('')
const passwordErrorMessage = ref('')
const isSubmitting = ref(false)

const validateEmail = () => {
  if (!email.value) {
    emailErrorMessage.value = '이메일을 입력해주세요.'
    return false
  }

  emailErrorMessage.value = ''
  return true
}

const validatePassword = () => {
  if (!password.value) {
    passwordErrorMessage.value = '비밀번호를 입력해주세요.'
    return false
  }

  if (password.value.length < 8) {
    passwordErrorMessage.value = '비밀번호는 8자 이상 입력해주세요.'
    return false
  }

  passwordErrorMessage.value = ''
  return true
}

const removeEmailError = () => {
  emailErrorMessage.value = ''
}

const removePasswordError = () => {
  passwordErrorMessage.value = ''
}

const handleForgotPassword = () => {
  alert('비밀번호 찾기 기능은 준비 중입니다.')
}

const handleLogin = async () => {
  if (isSubmitting.value) {
    return
  }

  const validEmail = validateEmail()
  const validPassword = validatePassword()

  if (!validEmail || !validPassword) {
    alert('로그인에 실패했습니다. 입력한 정보를 확인해주세요.')
    return
  }

  isSubmitting.value = true

  try {
    const response = await fetch(`${AUTH_API_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
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

      if (response.status === 401) {
        alert(data.error || '이메일 또는 비밀번호가 올바르지 않습니다.')
        return
      }

      alert('로그인에 실패했습니다.')
      return
    }

    const isAuthenticated = await login()
    if (!isAuthenticated) {
      alert('로그인 상태를 확인하지 못했습니다. 다시 시도해주세요.')
      return
    }

    alert('로그인 성공')
    router.push('/')
  } catch {
    alert('이메일 또는 비밀번호가 올바르지 않습니다.')
  } finally {
    isSubmitting.value = false
  }
}

const oauthLogin = (provider) => {
  window.location.href = `${AUTH_API_URL}/${provider}/`
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
  padding: 32px 20px 56px;
}

.login-shell {
  width: min(620px, 100%);
  margin-inline: auto;
}

.login-panel {
  border: 1px solid var(--color-border);
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgb(59 130 246 / 10%), transparent 34%),
    linear-gradient(180deg, rgb(255 255 255 / 98%), rgb(248 250 252 / 98%));
  padding: clamp(30px, 4vw, 40px);
  box-shadow: var(--shadow-lg);
}

.login-brand {
  display: grid;
  justify-items: center;
  gap: 12px;
  margin-bottom: 30px;
  text-align: center;
}

.login-brand__logo {
  width: min(148px, 38vw);
  max-height: 56px;
  height: auto;
}

.login-brand__description {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
  line-height: 1.5;
}

.login-form {
  display: grid;
  gap: 18px;
}

.field-group label {
  display: block;
  margin-bottom: 10px;
  color: var(--color-text);
  font-size: 1.05rem;
  font-weight: 700;
}

.field-group__label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.field-group__label-row label {
  margin-bottom: 0;
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

.ghost-link {
  appearance: none;
  border: none;
  background: none;
  padding: 0;
  color: #8b95a7;
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  white-space: nowrap;
}

.ghost-link:hover {
  color: var(--color-primary-600);
}

#login-btn {
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

#login-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  margin: 8px 0 0;
  color: var(--color-danger);
  font-size: 0.9rem;
}

.social-divider {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 14px;
  margin: 28px 0 20px;
  color: #9ca3af;
  font-style: normal;
}

.social-divider span {
  height: 1px;
  background-color: #e5e7eb;
}

.social-divider em {
  font-style: normal;
  font-size: 0.96rem;
}

.social-login {
  display: grid;
  gap: 14px;
}

.social-login__button {
  width: 100%;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  padding: 13px 18px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    filter var(--transition-fast);
}

.social-login__button:hover {
  transform: translateY(-1px);
}

.social-login__icon {
  position: absolute;
  left: 18px;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.social-login__icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

.social-login__button--kakao {
  border: none;
  background-color: #fee500;
  color: #181600;
  box-shadow: 0 14px 28px -22px rgb(254 229 0 / 90%);
}

.social-login__button--google {
  border: 1px solid #d1d5db;
  background-color: #fff;
  color: #111827;
}

.social-login__button--naver {
  border: none;
  background-color: #03c75a;
  color: #fff;
  box-shadow: 0 14px 28px -22px rgb(3 199 90 / 90%);
}

.social-login__icon--kakao {
  color: currentColor;
}

.social-login__icon--naver {
  color: currentColor;
}

#signup-link {
  display: block;
  width: fit-content;
  margin: 24px auto 0;
  color: var(--color-primary-600);
  font-weight: 700;
  text-decoration: none;
}

#signup-link:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .login-page {
    padding-inline: 14px;
  }

  .login-panel {
    border-radius: 24px;
    padding: 22px 18px;
  }

  .login-brand__logo {
    width: min(132px, 42vw);
  }

  .field-group__label-row {
    align-items: center;
    flex-direction: row;
    gap: 10px;
  }
}
</style>
