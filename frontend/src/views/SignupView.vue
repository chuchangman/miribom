<script setup>
import defaultProfile from '@/assets/images/default-profile.png'
import { ref } from 'vue'

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

function handleProfileImgChange(event) {
  const file = event.target.files[0]
  if (file) {
    profileImg.value = file
    previewImageUrl.value = URL.createObjectURL(file)
  } else {
    profileImg.value = null
    previewImageUrl.value = defaultProfile
  }
}

function validateNickname() {
  if (nickname.value.length < 3) {
    errorNickname.value = '닉네임은 최소 3자 이상이어야 합니다.'
    return false
  } else {
    errorNickname.value = ''
    return true
  }
}
function removeNicknameError() {
  errorNickname.value = ''
}

function validateEmail() {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(email.value)) {
    errorEmail.value = '유효한 이메일 주소를 입력해주세요.'
    return false
  } else {
    errorEmail.value = ''
    return true
  }
}
function removeEmailError() {
  errorEmail.value = ''
}

function validatePassword() {
  if (password.value.length < 8) {
    errorPassword.value = '비밀번호는 최소 8자 이상이어야 합니다.'
    return false
  } else {
    errorPassword.value = ''
    checkPasswordMatch()
    return true
  }
}
function removePasswordError() {
  errorPassword.value = ''
}

function removeConfirmPasswordError() {
  errorConfirmPassword.value = ''
}

function checkPasswordMatch() {
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
function changePassword() {
  if (confirmPassword.value) {
    checkPasswordMatch()
  }
}

function signup() {
  const validNickname = validateNickname()
  const validEmail = validateEmail()
  const validPassword = validatePassword()
  const passwordsMatch = checkPasswordMatch()
  if (validNickname && validEmail && validPassword && passwordsMatch) {
    alert('회원가입이 완료되었습니다.')
  } else {
    alert('입력한 정보를 확인해주세요.')
  }
}
</script>

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
    <button type="submit" id="signup-btn">회원가입</button>
  </form>
</template>

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
</style>
