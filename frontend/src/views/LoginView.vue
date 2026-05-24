<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const email = ref('')
const password = ref('')
const emailErrorMessage = ref('')
const passwordErrorMessage = ref('')

function validateEmail() {
  if (!email.value) {
    emailErrorMessage.value = '이메일을 입력해주세요.'
    return false
  } else {
    emailErrorMessage.value = ''
    return true
  }
}

function validatePassword() {
  if (!password.value) {
    passwordErrorMessage.value = '비밀번호를 입력해주세요.'
    return false
  } else if (password.value.length < 8) {
    passwordErrorMessage.value = '비밀번호는 8자 이상 입력해주세요.'
    return false
  } else {
    passwordErrorMessage.value = ''
    return true
  }
}

function removeEmailError() {
  emailErrorMessage.value = ''
}
function removePasswordError() {
  passwordErrorMessage.value = ''
}

function handleLogin() {
  const validEmail = validateEmail()
  const validPassword = validatePassword()

  if (validEmail && validPassword) {
    alert('로그인 성공!')
    console.log('이메일:', email.value)
    console.log('비밀번호:', password.value)
  } else {
    alert('로그인 실패! 입력한 정보를 확인해주세요.')
  }
  // 이 아래는 실제 로그인 API 정하면 수정할것
  //   axios({
  //     method:'POST',
  //     url:'/api/login/',
  //     headers: {
  //     },
  //     data: {
  //       email: email.value,
  //       password: password.value
  //     }
  //   }).then((response) => {
  //     console.log(response.data);
  //   })
}
</script>

<template>
  <h1>로그인페이지</h1>
  <form class="login-form" @submit.prevent="handleLogin">
    <div>
      <label for="email">이메일:</label>
      <input
        type="email"
        id="email"
        v-model.trim="email"
        @blur="validateEmail"
        @focus="removeEmailError"
      />
      <p class="error-message" v-if="emailErrorMessage">{{ emailErrorMessage }}</p>
      <label for="password">비밀번호:</label>
      <input
        type="password"
        id="password"
        v-model.trim="password"
        @blur="validatePassword"
        @focus="removePasswordError"
      />
      <p class="error-message" v-if="passwordErrorMessage">{{ passwordErrorMessage }}</p>
    </div>
    <button id="login-btn" type="submit">로그인</button>
  </form>
  <RouterLink to="/signup" id="signup-link">계정이 없으신가요?</RouterLink><br />
  <section>
    <button id="google-login-btn" type="button">Google로 로그인</button>
    <button id="naver-login-btn" type="button">Naver로 로그인</button>
    <button id="kakao-login-btn" type="button">Kakao로 로그인</button>
  </section>
</template>

<style scoped>
h1 {
  text-align: center;
  margin-top: 50px;
}
.login-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-form div {
  margin-bottom: 20px;
}
.login-form label {
  display: block;
  margin-bottom: 5px;
}
.login-form input {
  width: 200px;
  padding: 8px;
  margin-bottom: 10px;
}
#login-btn {
  padding: 10px 20px;
  background-color: #008cba;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}
#login-btn:hover {
  background-color: #007bb5;
}
.error-message {
  margin-top: -10px;
  color: red;
}
#signup-link {
  display: block;
  text-align: center;
  margin-top: 10px;
  color: #008cba;
  text-decoration: none;
}
#signup-link:hover {
  text-decoration: underline;
}
section {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
section #google-login-btn {
  padding: 10px 20px;
  border-radius: 5px;
  background-color: #db4437;
  color: white;
  border: none;
  cursor: pointer;
  margin-bottom: 10px;
}
section #naver-login-btn {
  padding: 10px 20px;
  border-radius: 5px;
  background-color: #03c75a;
  color: white;
  border: none;
  cursor: pointer;
  margin-bottom: 10px;
}
section #kakao-login-btn {
  padding: 10px 20px;
  border-radius: 5px;
  background-color: #fee500;
  color: #3c1e1e;
  border: none;
  cursor: pointer;
  margin-bottom: 10px;
}
section button:hover {
  filter: brightness(90%);
}
</style>
