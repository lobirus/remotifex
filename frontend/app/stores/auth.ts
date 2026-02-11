import type { LoginResponse, User } from '~/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  function setAuth(response: LoginResponse) {
    token.value = response.access_token
    user.value = response.user
    if (import.meta.client) {
      localStorage.setItem('remotifex_token', response.access_token)
      localStorage.setItem('remotifex_user', JSON.stringify(response.user))
    }
  }

  function logout() {
    token.value = null
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem('remotifex_token')
      localStorage.removeItem('remotifex_user')
    }
  }

  function loadFromStorage() {
    if (import.meta.client) {
      const savedToken = localStorage.getItem('remotifex_token')
      const savedUser = localStorage.getItem('remotifex_user')
      if (savedToken && savedUser) {
        token.value = savedToken
        try {
          user.value = JSON.parse(savedUser)
        } catch {
          logout()
        }
      }
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    setAuth,
    logout,
    loadFromStorage,
  }
})
