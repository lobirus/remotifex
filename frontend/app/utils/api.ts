/**
 * API client helper for making authenticated requests to the backend.
 */

export function useApi() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const baseUrl = config.public.apiUrl

  async function request<T>(
    path: string,
    options: {
      method?: string
      body?: unknown
      query?: Record<string, string>
    } = {},
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (authStore.token) {
      headers.Authorization = `Bearer ${authStore.token}`
    }

    const url = new URL(`${baseUrl}${path}`, window.location.origin)
    if (options.query) {
      for (const [key, value] of Object.entries(options.query)) {
        url.searchParams.set(key, value)
      }
    }

    const response = await fetch(url.toString(), {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    })

    if (response.status === 401) {
      authStore.logout()
      navigateTo('/login')
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) {
      return undefined as T
    }

    return response.json()
  }

  return {
    get: <T>(path: string, query?: Record<string, string>) =>
      request<T>(path, { query }),

    post: <T>(path: string, body?: unknown) =>
      request<T>(path, { method: 'POST', body }),

    put: <T>(path: string, body?: unknown) =>
      request<T>(path, { method: 'PUT', body }),

    patch: <T>(path: string, body?: unknown) =>
      request<T>(path, { method: 'PATCH', body }),

    delete: <T>(path: string) =>
      request<T>(path, { method: 'DELETE' }),
  }
}
