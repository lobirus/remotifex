/**
 * Global auth middleware: redirects unauthenticated users to login,
 * and checks setup status on first load.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  // Skip for login and setup pages
  if (to.path === '/login' || to.path === '/setup') return

  const authStore = useAuthStore()

  // Load auth from localStorage on first visit
  if (!authStore.isAuthenticated) {
    authStore.loadFromStorage()
  }

  // Check setup status for first-time visitors
  if (!authStore.isAuthenticated) {
    try {
      const config = useRuntimeConfig()
      const response = await fetch(`${config.public.apiUrl}/settings/setup-status`)
      const data = await response.json()

      if (!data.setup_completed) {
        return navigateTo('/setup')
      }
    } catch {
      // API not available, continue to login
    }

    return navigateTo('/login')
  }
})
