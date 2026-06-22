<template>
  <h1>프로필 편집</h1>
  <form class="profile-edit-form" @submit.prevent="saveProfile">
    <label for="nickname">닉네임</label>
    <input
      type="text"
      id="nickname"
      v-model.trim="nickname"
      :disabled="isSaving"
      @focus="removeNicknameError"
      @blur="validateNickname"
    />
    <p v-if="errorNickname" class="error-message">{{ errorNickname }}</p>
    <p v-if="saveErrorMessage" class="error-message">{{ saveErrorMessage }}</p>
    <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
    <p class="help-message">프로필 이미지는 추후 연결 예정입니다.</p>
    <button type="submit" id="save-profile-btn" :disabled="isSaving">
      {{ isSaving ? '저장 중...' : '변경사항 저장' }}
    </button>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, updateProfile } = useAuth()
const nickname = ref(user.value?.nickname || '')
const errorNickname = ref('')
const saveErrorMessage = ref('')
const successMessage = ref('')
const isSaving = ref(false)

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

const saveProfile = async () => {
  const validNickname = validateNickname()
  if (!validNickname || isSaving.value) {
    return
  }

  isSaving.value = true
  saveErrorMessage.value = ''
  successMessage.value = ''

  try {
    await updateProfile({ nickname: nickname.value })
    successMessage.value = '프로필이 수정되었습니다.'
    router.push('/mypage')
  } catch (error) {
    saveErrorMessage.value = error.message || '프로필 수정에 실패했습니다.'
  } finally {
    isSaving.value = false
  }
}

watch(
  user,
  (nextUser) => {
    nickname.value = nextUser?.nickname || ''
  },
  { immediate: true },
)
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
  margin-top: -4px;
  color: red;
}

.success-message {
  color: #059669;
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

#save-profile-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
