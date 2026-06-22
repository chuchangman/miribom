import { ref } from 'vue'
import { AUTH_API_URL } from '@/config/api'
import { updateMyProfile } from '@/services/authApi.js'

const isLogin = ref(false)
const user = ref(null)
const isAuthInitialized = ref(false)
let authCheckPromise = null

export const useAuth = () => {
  const resetAuth = () => {
    isLogin.value = false
    user.value = null
  }

  const requestMe = () => {
    return fetch(`${AUTH_API_URL}/me/`, {
      method: 'GET',
      credentials: 'include',
    })
  }

  const refreshAccessToken = async () => {
    try {
      const response = await fetch(`${AUTH_API_URL}/refresh/`, {
        method: 'POST',
        credentials: 'include',
      })

      return response.ok
    } catch {
      return false
    }
  }

  const performAuthCheck = async () => {
    try {
      let response = await requestMe()

      if (response.status === 401) {
        const isRefreshed = await refreshAccessToken()

        if (!isRefreshed) {
          resetAuth()
          return false
        }

        response = await requestMe()
      }

      if (!response.ok) {
        resetAuth()
        return false
      }

      const data = await response.json()
      isLogin.value = true
      user.value = data
      return true
    } catch {
      resetAuth()
      return false
    } finally {
      isAuthInitialized.value = true
    }
  }

  const checkAuth = (force = false) => {
    if (authCheckPromise) {
      return authCheckPromise
    }

    if (isAuthInitialized.value && !force) {
      return Promise.resolve(isLogin.value)
    }

    authCheckPromise = performAuthCheck().finally(() => {
      authCheckPromise = null
    })

    return authCheckPromise
  }

  const login = async () => {
    return await checkAuth(true)
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

      resetAuth()
      isAuthInitialized.value = true
      return true
    } catch {
      return false
    }
  }

  const updateProfile = async ({ nickname }) => {
    const updatedUser = await updateMyProfile({ nickname })
    user.value = updatedUser
    isLogin.value = true
    isAuthInitialized.value = true
    return updatedUser
  }

  return {
    checkAuth,
    isLogin,
    isAuthInitialized,
    user,
    login,
    logout,
    updateProfile,
  }
}
