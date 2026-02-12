<script setup lang="ts">
import type { LoginResponse } from '~/types'

definePageMeta({ layout: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''

  if (!username.value.trim() || !password.value) {
    errorMessage.value = 'Please enter your username and password.'
    return
  }

  loading.value = true
  try {
    const response = await api.post<LoginResponse>('/auth/login', {
      username: username.value.trim(),
      password: password.value,
    })
    authStore.setAuth(response)
    toast.success('Welcome back!')
    await navigateTo('/')
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Login failed'
    errorMessage.value = message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md animate-fade-in">
    <!-- Branding -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600 mb-4">
        <svg class="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-heading">Welcome back</h1>
      <p class="mt-1 text-sm text-muted">Sign in to your Remotifex account</p>
    </div>

    <!-- Login Card -->
    <div class="card p-8">
      <form @submit.prevent="handleLogin" class="space-y-5">
        <!-- Error Message -->
        <div
          v-if="errorMessage"
          class="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm animate-fade-in"
        >
          <svg class="w-5 h-5 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-sub mb-1.5">
            Username
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="Enter your username"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-sub mb-1.5">
            Password
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Enter your password"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <!-- Submit -->
        <UiButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="loading"
          class="w-full"
        >
          Sign in
        </UiButton>
      </form>
    </div>

    <!-- Footer -->
    <p class="mt-6 text-center text-xs text-faint">
      Remotifex — AI-powered remote development
    </p>
  </div>
</template>
