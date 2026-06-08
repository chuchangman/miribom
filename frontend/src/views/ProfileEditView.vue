<template>
  <h1>프로필 편집</h1>
  <form @submit.prevent="signup" class="profile-edit-form">
    <label for="nickname">닉네임</label>
    <input
      type="text"
      id="nickname"
      v-model.trim="nickname"
      @focus="removeNicknameError"
      @blur="validateNickname"
    />
    <p class="error-message" v-if="errorNickname">{{ errorNickname }}</p>
    <p class="help-message">프로필 저장 API 연결 전까지 입력값 검증만 진행합니다.</p>
    <button type="submit" id="save-profile-btn">변경사항 저장</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()
const nickname = ref(user.value?.nickname || '')

const errorNickname = ref('')

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

function signup() {
  const validNickname = validateNickname()
  if (!validNickname) {
    alert('입력한 정보를 확인해주세요.')
    return
  }

  console.log('변경할 닉네임:', nickname.value)
  alert('프로필 수정 입력값 확인 완료')
}
</script>

<style scoped>
.profile-edit-form {
  display: flex;
  flex-direction: column;
  align-items: center;
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
.help-message {
  color: #6b7280;
  font-size: 14px;
}
#save-profile-btn {
  padding: 10px 20px;
  background-color: #008cba;
  color: white;
  border: none;
  cursor: pointer;
}
#save-profile-btn:hover {
  background-color: #007bb5;
}
</style>
