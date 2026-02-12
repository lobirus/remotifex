<script setup lang="ts">
import type { LoginResponse, ServerInfo } from '~/types'

definePageMeta({ layout: 'auth' })

const authStore = useAuthStore()
const api = useApi()
const toast = useToast()

// Wizard state
const currentStep = ref(1)
const totalSteps = 4
const loading = ref(false)
const errorMessage = ref('')

// Step 1: Admin account
const adminUsername = ref('')
const adminPassword = ref('')
const adminPasswordConfirm = ref('')

// Step 2: AI configuration
const claudeApiKey = ref('')
const claudeModel = ref('claude-sonnet-4-5-20250929')
const ampApiKey = ref('')

const modelOptions = [
  { value: 'claude-sonnet-4-5-20250929', label: 'Claude Sonnet 4.5' },
  { value: 'claude-opus-4-6', label: 'Claude Opus 4.6' },
]

// Step 3: Access configuration
const serverInfo = ref<ServerInfo | null>(null)
const configureAccess = ref(false)
const remotifexDomain = ref('')
const customPort = ref<number | undefined>(undefined)

// Computed progress
const progressPercent = computed(() => ((currentStep.value - 1) / (totalSteps - 1)) * 100)

// Load server info when entering step 3
async function loadServerInfo() {
  try {
    serverInfo.value = await api.get<ServerInfo>('/settings/server-info')
  } catch {
    // Non-critical — we just won't show the IP
  }
}

// Step 1: Create admin account
async function createAdmin() {
  errorMessage.value = ''

  if (!adminUsername.value.trim()) {
    errorMessage.value = 'Please enter a username.'
    return
  }
  if (adminPassword.value.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters.'
    return
  }
  if (adminPassword.value !== adminPasswordConfirm.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  loading.value = true
  try {
    const response = await api.post<LoginResponse>('/auth/setup', {
      username: adminUsername.value.trim(),
      password: adminPassword.value,
    })
    authStore.setAuth(response)
    toast.success('Admin account created!')
    currentStep.value = 2
    errorMessage.value = ''
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to create admin account'
  } finally {
    loading.value = false
  }
}

// Step 2: Configure AI → move to step 3 (access)
async function configureAI() {
  errorMessage.value = ''

  if (!claudeApiKey.value.trim()) {
    errorMessage.value = 'Please enter your Claude API key.'
    return
  }

  // Save AI settings first, but don't complete setup yet
  loading.value = true
  try {
    await api.patch('/settings/ai', {
      claude_api_key: claudeApiKey.value.trim(),
      claude_default_model: claudeModel.value,
      ...(ampApiKey.value.trim() ? { amp_api_key: ampApiKey.value.trim() } : {}),
    })
    toast.success('AI configuration saved!')
    currentStep.value = 3
    errorMessage.value = ''
    // Load server info for access step
    loadServerInfo()
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to save AI configuration'
  } finally {
    loading.value = false
  }
}

// Step 3: Save access settings & complete setup
async function completeSetup() {
  errorMessage.value = ''
  loading.value = true
  try {
    const payload: Record<string, unknown> = {
      ai_settings: {
        claude_api_key: claudeApiKey.value.trim(),
        claude_default_model: claudeModel.value,
        ...(ampApiKey.value.trim() ? { amp_api_key: ampApiKey.value.trim() } : {}),
      },
    }

    // Include access settings if user configured them
    if (configureAccess.value && remotifexDomain.value.trim()) {
      payload.access_settings = {
        remotifex_domain: remotifexDomain.value.trim(),
        ...(customPort.value ? { port: customPort.value } : {}),
      }
    }

    await api.post('/settings/complete-setup', payload)
    toast.success('Setup complete!')
    currentStep.value = 4
    errorMessage.value = ''
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to complete setup'
  } finally {
    loading.value = false
  }
}

function skipAccessConfig() {
  completeSetup()
}

function goToDashboard() {
  navigateTo('/')
}
</script>

<template>
  <div class="w-full max-w-lg animate-fade-in">
    <!-- Branding -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600 shadow-lg shadow-brand-600/20 mb-4">
        <svg class="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-heading">Set up Remotifex</h1>
      <p class="mt-2 text-sm text-muted">Let's get everything configured in a few quick steps</p>
    </div>

    <!-- Step Indicator -->
    <div class="flex items-center justify-center mb-8">
      <template v-for="step in totalSteps" :key="step">
        <!-- Step circle -->
        <div
          class="relative flex items-center justify-center w-8 h-8 rounded-full text-xs font-semibold transition-all duration-300"
          :class="[
            step < currentStep ? 'bg-brand-600 text-white shadow-sm' : '',
            step === currentStep ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/30' : '',
            step > currentStep ? 'bg-inset text-faint border border-edge' : '',
          ]"
        >
          <svg v-if="step < currentStep" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span v-else>{{ step }}</span>
        </div>
        <!-- Connector line -->
        <div
          v-if="step < totalSteps"
          class="w-10 h-px mx-1 transition-colors duration-300"
          :class="step < currentStep ? 'bg-brand-600' : 'bg-edge'"
        />
      </template>
    </div>

    <!-- Card -->
    <div class="card p-8">
      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="flex items-start gap-3 p-3 mb-6 rounded-lg bg-red-50 border border-red-200 dark:bg-red-950 dark:border-red-800 text-red-700 dark:text-red-400 text-sm animate-fade-in"
      >
        <svg class="w-5 h-5 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Step 1: Create Admin Account -->
      <div v-if="currentStep === 1" class="animate-fade-in">
        <h2 class="text-lg font-semibold text-heading mb-1">Create Admin Account</h2>
        <p class="text-sm text-muted mb-6">
          This will be the primary administrator account for your Remotifex instance.
        </p>

        <form @submit.prevent="createAdmin" class="space-y-4">
          <div>
            <label for="admin-username" class="block text-sm font-medium text-sub mb-1.5">
              Username
            </label>
            <input
              id="admin-username"
              v-model="adminUsername"
              type="text"
              autocomplete="username"
              placeholder="Choose a username"
              class="input-field"
              :disabled="loading"
            />
          </div>

          <div>
            <label for="admin-password" class="block text-sm font-medium text-sub mb-1.5">
              Password
            </label>
            <input
              id="admin-password"
              v-model="adminPassword"
              type="password"
              autocomplete="new-password"
              placeholder="At least 8 characters"
              class="input-field"
              :disabled="loading"
            />
          </div>

          <div>
            <label for="admin-password-confirm" class="block text-sm font-medium text-sub mb-1.5">
              Confirm Password
            </label>
            <input
              id="admin-password-confirm"
              v-model="adminPasswordConfirm"
              type="password"
              autocomplete="new-password"
              placeholder="Re-enter your password"
              class="input-field"
              :disabled="loading"
            />
          </div>

          <UiButton
            type="submit"
            variant="primary"
            size="lg"
            :loading="loading"
            class="w-full mt-4"
          >
            Create Account & Continue
          </UiButton>
        </form>
      </div>

      <!-- Step 2: Configure AI -->
      <div v-if="currentStep === 2" class="animate-fade-in">
        <h2 class="text-lg font-semibold text-heading mb-1">Configure AI</h2>
        <p class="text-sm text-muted mb-6">
          Connect your AI provider to power Remotifex's development capabilities.
        </p>

        <form @submit.prevent="configureAI" class="space-y-4">
          <div>
            <label for="claude-api-key" class="block text-sm font-medium text-sub mb-1.5">
              Claude API Key
            </label>
            <input
              id="claude-api-key"
              v-model="claudeApiKey"
              type="password"
              placeholder="sk-ant-..."
              class="input-field font-mono text-sm"
              :disabled="loading"
            />
            <p class="mt-1.5 text-xs text-faint">
              Get your API key from
              <a href="https://console.anthropic.com/" target="_blank" rel="noopener" class="text-brand-600 hover:text-brand-700 underline">console.anthropic.com</a>
            </p>
          </div>

          <div>
            <label for="claude-model" class="block text-sm font-medium text-sub mb-1.5">
              Default Model
            </label>
            <select
              id="claude-model"
              v-model="claudeModel"
              class="input-field"
              :disabled="loading"
            >
              <option
                v-for="option in modelOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <div>
            <label for="amp-api-key" class="block text-sm font-medium text-sub mb-1.5">
              Amp API Key
              <span class="text-faint font-normal">(optional)</span>
            </label>
            <input
              id="amp-api-key"
              v-model="ampApiKey"
              type="password"
              placeholder="Optional — for Amp tool integration"
              class="input-field font-mono text-sm"
              :disabled="loading"
            />
          </div>

          <UiButton
            type="submit"
            variant="primary"
            size="lg"
            :loading="loading"
            class="w-full mt-4"
          >
            Save & Continue
          </UiButton>
        </form>
      </div>

      <!-- Step 3: Access Configuration -->
      <div v-if="currentStep === 3" class="animate-fade-in">
        <h2 class="text-lg font-semibold text-heading mb-1">Access Configuration</h2>
        <p class="text-sm text-muted mb-6">
          Configure how you'll access Remotifex. You can skip this to use the default IP-based access.
        </p>

        <!-- Server info -->
        <div v-if="serverInfo?.ip" class="p-3 rounded-lg bg-inset border border-edge mb-5">
          <p class="text-sm text-muted">
            Your server is accessible at
          </p>
          <p class="text-sm font-mono font-medium text-heading mt-0.5">
            http://{{ serverInfo.ip }}
          </p>
        </div>

        <!-- Toggle domain config -->
        <div class="mb-5">
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              v-model="configureAccess"
              type="checkbox"
              class="h-4 w-4 rounded border-edge text-brand-600 focus:ring-brand-500"
            />
            <span class="text-sm font-medium text-sub">
              Set up a custom domain for Remotifex
            </span>
          </label>
        </div>

        <!-- Domain configuration (conditional) -->
        <div v-if="configureAccess" class="space-y-4 mb-6 animate-fade-in">
          <div>
            <label for="remotifex-domain" class="block text-sm font-medium text-sub mb-1.5">
              Domain
            </label>
            <input
              id="remotifex-domain"
              v-model="remotifexDomain"
              type="text"
              placeholder="e.g. remotifex.example.com"
              class="input-field"
            />
            <div v-if="remotifexDomain.trim() && serverInfo?.ip" class="mt-2 p-3 rounded-lg bg-blue-50 border border-blue-200 dark:bg-blue-950 dark:border-blue-800">
              <p class="text-xs font-medium text-blue-800 dark:text-blue-300 mb-1">DNS Configuration</p>
              <p class="text-xs text-blue-700 dark:text-blue-400">
                Point an <span class="font-mono font-semibold">A</span> record for
                <span class="font-mono font-semibold">{{ remotifexDomain }}</span>
                to <span class="font-mono font-semibold">{{ serverInfo.ip }}</span>
              </p>
            </div>
          </div>

          <div>
            <label for="custom-port" class="block text-sm font-medium text-sub mb-1.5">
              Port
              <span class="text-faint font-normal">(optional, default 80)</span>
            </label>
            <input
              id="custom-port"
              v-model.number="customPort"
              type="number"
              min="1"
              max="65535"
              placeholder="80"
              class="input-field"
            />
          </div>
        </div>

        <div class="flex gap-3">
          <UiButton
            variant="ghost"
            size="lg"
            class="flex-1"
            :disabled="loading"
            @click="skipAccessConfig"
          >
            Skip
          </UiButton>
          <UiButton
            v-if="configureAccess"
            variant="primary"
            size="lg"
            :loading="loading"
            class="flex-1"
            @click="completeSetup"
          >
            Save & Complete
          </UiButton>
        </div>
      </div>

      <!-- Step 4: All Set -->
      <div v-if="currentStep === 4" class="animate-fade-in text-center py-4">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 mb-5">
          <svg class="w-8 h-8 text-green-600 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </div>

        <h2 class="text-lg font-semibold text-heading mb-2">You're all set!</h2>
        <p class="text-sm text-muted mb-8 max-w-sm mx-auto">
          Remotifex is configured and ready to go. Create your first project and start building with AI.
        </p>

        <UiButton
          variant="primary"
          size="lg"
          class="w-full"
          @click="goToDashboard"
        >
          Go to Dashboard
        </UiButton>
      </div>
    </div>

    <!-- Footer -->
    <p class="mt-6 text-center text-xs text-faint">
      Step {{ currentStep }} of {{ totalSteps }}
    </p>
  </div>
</template>
