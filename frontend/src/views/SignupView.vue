<template>
  <h1>회원가입페이지</h1>
  <form @submit.prevent="signup" class="signup-form">
    <label for="profile-img">프로필 이미지</label>
    <img :src="previewImageUrl" alt="프로필 이미지 미리보기" class="profile-preview" />
    <input
      type="file"
      accept="image/*"
      name="profile-img"
      id="profile-img"
      @change="handleProfileImgChange"
    />
    <label for="nickname">닉네임</label>
    <input
      type="text"
      id="nickname"
      v-model.trim="nickname"
      @focus="removeNicknameError"
      @blur="validateNickname"
    />
    <p class="error-message" v-if="errorNickname">{{ errorNickname }}</p>
    <label for="email">이메일</label>
    <input
      type="email"
      id="email"
      v-model.trim="email"
      @focus="removeEmailError"
      @blur="validateEmail"
    />
    <p class="error-message" v-if="errorEmail">{{ errorEmail }}</p>
    <label for="password">비밀번호</label>
    <input
      type="password"
      id="password"
      v-model="password"
      @focus="removePasswordError"
      @blur="validatePassword"
      @input="changePassword"
    />
    <p class="error-message" v-if="errorPassword">{{ errorPassword }}</p>
    <label for="confirm-password">비밀번호 확인</label>
    <input
      type="password"
      id="confirm-password"
      v-model="confirmPassword"
      @focus="removeConfirmPasswordError"
      @blur="checkPasswordMatch"
    />
    <p class="error-message" v-if="errorConfirmPassword">{{ errorConfirmPassword }}</p>
    <button type="submit" id="signup-btn" :disabled="isSubmitting">
      {{ isSubmitting ? '가입 처리 중...' : '회원가입' }}
    </button>
  </form>
</template>

<script setup>
import defaultProfile from '@/assets/images/default-profile.png'
import { ref } from 'vue'
import { AUTH_API_URL } from '@/config/api'
import { useRouter } from 'vue-router'
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
  } else {
    profileImg.value = null
    previewImageUrl.value = defaultProfile
  }
}

const validateNickname = () => {
  if (nickname.value.length < 3) {
    errorNickname.value = '닉네임은 최소 3자 이상이어야 합니다.'
    return false
  } else {
    errorNickname.value = ''
    return true
  }
}
const removeNicknameError = () => {
  errorNickname.value = ''
}

const validateEmail = () => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(email.value)) {
    errorEmail.value = '유효한 이메일 주소를 입력해주세요.'
    return false
  } else {
    errorEmail.value = ''
    return true
  }
}
const removeEmailError = () => {
  errorEmail.value = ''
}

const validatePassword = () => {
  if (password.value.length < 8) {
    errorPassword.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return false
  } else {
    errorPassword.value = ''
    checkPasswordMatch()
    return true
  }
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
  } else if (password.value !== confirmPassword.value) {
    errorConfirmPassword.value = '비밀번호가 일치하지 않습니다.'
    return false
  } else {
    errorConfirmPassword.value = ''
    return true
  }
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

    router.push('/living-profile')
  } catch {
    alert('회원가입 실패')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.signup-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.profile-preview {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
}
label {
  display: block;
  margin-bottom: 5px;
}
input {
  width: 200px;
  padding: 8px;
  margin-bottom: 10px;
}
.error-message {
  margin-top: -10px;
  color: red;
}
#signup-btn {
  padding: 10px 20px;
  background-color: #008cba;
  color: white;
  border: none;
  cursor: pointer;
}
#signup-btn:hover {
  background-color: #007bb5;
}
#signup-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
