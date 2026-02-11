<template>
  <div class="max-w-3xl mx-auto p-6 space-y-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">Settings</h1>
      <p class="mt-1 text-sm text-gray-500">Manage your Remotifex configuration</p>
    </div>

    <!-- AI Configuration -->
    <section class="card p-6 space-y-4">
      <h2 class="text-lg font-medium text-gray-900">AI Configuration</h2>
      <p class="text-sm text-gray-500">Configure your AI coding assistant</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Claude API Key</label>
          <div class="flex gap-2">
            <input
              v-model="claudeApiKey"
              type="password"
              :placeholder="settings?.ai?.claude_api_key_set ? '••••••••••• (key is set)' : 'sk-ant-...'"
              class="input-field flex-1"
            />
            <button class="btn-primary btn-sm" @click="updateApiKey">
              {{ settings?.ai?.claude_api_key_set ? 'Update' : 'Save' }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Default Model</label>
          <select v-model="defaultModel" class="input-field" @change="updateModel">
            <option value="sonnet">Claude Sonnet 4.5</option>
            <option value="opus">Claude Opus 4.6</option>
            <option value="haiku">Claude Haiku 4.5</option>
          </select>
        </div>
      </div>
    </section>

    <!-- Remotifex Access -->
    <section class="card p-6 space-y-4">
      <h2 class="text-lg font-medium text-gray-900">Remotifex Access</h2>
      <p class="text-sm text-gray-500">Configure how you access the Remotifex dashboard</p>

      <div class="space-y-4">
        <!-- Server IP (read-only) -->
        <div v-if="serverInfo?.ip" class="p-3 rounded-lg bg-gray-50 border border-gray-200">
          <p class="text-xs font-medium text-gray-500 mb-0.5">Server IP</p>
          <p class="text-sm font-mono text-gray-900">{{ serverInfo.ip }}</p>
        </div>

        <!-- Current access URL -->
        <div v-if="serverInfo?.current_url" class="p-3 rounded-lg bg-gray-50 border border-gray-200">
          <p class="text-xs font-medium text-gray-500 mb-0.5">Current Access URL</p>
          <p class="text-sm font-mono text-gray-900">{{ serverInfo.current_url }}</p>
        </div>

        <!-- Remotifex domain -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Custom Domain
            <span class="text-gray-400 font-normal">(optional)</span>
          </label>
          <input
            v-model="remotifexDomain"
            type="text"
            placeholder="e.g. remotifex.example.com"
            class="input-field"
          />
          <div v-if="remotifexDomain.trim() && serverInfo?.ip" class="mt-2 p-3 rounded-lg bg-blue-50 border border-blue-200">
            <p class="text-xs font-medium text-blue-800 mb-1">DNS Configuration</p>
            <p class="text-xs text-blue-700">
              Point an <span class="font-mono font-semibold">A</span> record for
              <span class="font-mono font-semibold">{{ remotifexDomain }}</span>
              to <span class="font-mono font-semibold">{{ serverInfo.ip }}</span>
            </p>
          </div>
        </div>

        <!-- Port -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Port
            <span class="text-gray-400 font-normal">(default 80)</span>
          </label>
          <input
            v-model.number="accessPort"
            type="number"
            min="1"
            max="65535"
            placeholder="80"
            class="input-field w-32"
          />
        </div>

        <button class="btn-primary btn-sm" @click="updateAccess">Save Access Settings</button>
      </div>
    </section>

    <!-- Project Domains -->
    <section class="card p-6 space-y-4">
      <h2 class="text-lg font-medium text-gray-900">Project Domains</h2>
      <p class="text-sm text-gray-500">Configure the base domain for project staging and production environments</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Base Domain</label>
          <input
            v-model="baseDomain"
            type="text"
            placeholder="projects.example.com"
            class="input-field"
          />
          <p class="mt-1 text-xs text-gray-400">Projects will be available at {slug}.{{ baseDomain || 'projects.example.com' }}</p>
          <div v-if="baseDomain.trim() && serverInfo?.ip" class="mt-2 p-3 rounded-lg bg-blue-50 border border-blue-200">
            <p class="text-xs font-medium text-blue-800 mb-1">DNS Configuration</p>
            <p class="text-xs text-blue-700">
              Point a wildcard <span class="font-mono font-semibold">A</span> record for
              <span class="font-mono font-semibold">*.{{ baseDomain }}</span>
              to <span class="font-mono font-semibold">{{ serverInfo.ip }}</span>
            </p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SSL Email</label>
          <input
            v-model="sslEmail"
            type="email"
            placeholder="admin@example.com"
            class="input-field"
          />
          <p class="mt-1 text-xs text-gray-400">Used for Let's Encrypt SSL certificates</p>
        </div>

        <button class="btn-primary btn-sm" @click="updateDomain">Save Domain Settings</button>
      </div>
    </section>

    <!-- API & MCP -->
    <section class="card p-6 space-y-4">
      <h2 class="text-lg font-medium text-gray-900">Integrations</h2>
      <p class="text-sm text-gray-500">External API and MCP server (coming soon)</p>

      <div class="space-y-3 opacity-50">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">REST API</p>
            <p class="text-xs text-gray-400">Enable external API access</p>
          </div>
          <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Coming soon</span>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">MCP Server</p>
            <p class="text-xs text-gray-400">Enable Model Context Protocol server</p>
          </div>
          <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">Coming soon</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { AppSettings, ServerInfo } from '~/types'

definePageMeta({ layout: 'default' })

const api = useApi()
const toast = useToast()
const settings = ref<AppSettings | null>(null)
const serverInfo = ref<ServerInfo | null>(null)
const claudeApiKey = ref('')
const defaultModel = ref('sonnet')
const remotifexDomain = ref('')
const accessPort = ref<number | undefined>(undefined)
const baseDomain = ref('')
const sslEmail = ref('')

onMounted(async () => {
  try {
    const [settingsData, serverData] = await Promise.all([
      api.get<AppSettings>('/settings'),
      api.get<ServerInfo>('/settings/server-info'),
    ])
    settings.value = settingsData
    serverInfo.value = serverData
    defaultModel.value = settingsData.ai?.claude_default_model || 'sonnet'
    remotifexDomain.value = settingsData.access?.remotifex_domain || ''
    accessPort.value = settingsData.access?.port || undefined
    baseDomain.value = settingsData.domain?.base_domain || ''
    sslEmail.value = settingsData.domain?.ssl_email || ''
  } catch {
    // Settings not available
  }
})

async function updateApiKey() {
  if (!claudeApiKey.value) return
  try {
    await api.patch('/settings/ai', { claude_api_key: claudeApiKey.value })
    claudeApiKey.value = ''
    settings.value = await api.get<AppSettings>('/settings')
    toast.success('API key updated')
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'Failed to update API key')
  }
}

async function updateModel() {
  try {
    await api.patch('/settings/ai', { claude_default_model: defaultModel.value })
    toast.success('Model updated')
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'Failed to update model')
  }
}

async function updateAccess() {
  try {
    await api.patch('/settings/access', {
      remotifex_domain: remotifexDomain.value.trim() || undefined,
      port: accessPort.value || undefined,
    })
    serverInfo.value = await api.get<ServerInfo>('/settings/server-info')
    toast.success('Access settings saved')
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'Failed to save access settings')
  }
}

async function updateDomain() {
  try {
    await api.patch('/settings/domain', {
      base_domain: baseDomain.value.trim() || undefined,
      ssl_email: sslEmail.value.trim() || undefined,
    })
    toast.success('Domain settings saved')
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'Failed to save domain settings')
  }
}
</script>
