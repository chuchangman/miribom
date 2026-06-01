import { ref } from 'vue'

const isLogin = ref(!!localStorage.getItem('accessToken'))

export const useAuth = () => {
  const login = (access, refresh) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    isLogin.value = true
  }

  const logout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    isLogin.value = false
  }

  return {
    isLogin,
    login,
    logout,
  }
}
