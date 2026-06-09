import { ref } from 'vue'
import { AUTH_API_URL } from '@/config/api'
const isLogin = ref(false)
const user = ref(null)

export const useAuth = () => {
  const checkAuth = async () => {
    try {
      const response = await fetch(`${AUTH_API_URL}/me/`, {
        method: 'GET',
        credentials: 'include',
      })
      const data = await response.json()
      if (!response.ok) {
        isLogin.value = false
        user.value = null
        return false
      }
      isLogin.value = true
      user.value = data
      return true
    } catch (error) {
      isLogin.value = false
      user.value = null
      return false
    }
  }

  const login = async () => {
    return await checkAuth()
  }

  const logout = async () => {
    try {
      const response = await fetch(`${AUTH_API_URL}/logout/`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok) {
        return false
      }

      isLogin.value = false
      user.value = null
      return true
    } catch (error) {
      return false
    }
  }

  return {
    checkAuth,
    isLogin,
    user,
    login,
    logout,
  }
}
