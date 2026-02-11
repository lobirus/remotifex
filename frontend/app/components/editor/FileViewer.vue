<script setup lang="ts">
import type { FileContent } from '~/types'

interface Props {
  projectId: string
  path: string
  env?: string
}

const props = withDefaults(defineProps<Props>(), {
  env: 'staging',
})

const api = useApi()

const fileContent = ref<FileContent | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const filename = computed(() => {
  const parts = props.path.split('/')
  return parts[parts.length - 1] || props.path
})

const languageLabel = computed(() => {
  if (!fileContent.value?.language) return 'Plain text'
  const labels: Record<string, string> = {
    typescript: 'TypeScript',
    javascript: 'JavaScript',
    python: 'Python',
    vue: 'Vue',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    toml: 'TOML',
    markdown: 'Markdown',
    rust: 'Rust',
    go: 'Go',
    ruby: 'Ruby',
    sql: 'SQL',
    shell: 'Shell',
    bash: 'Bash',
    dockerfile: 'Dockerfile',
    xml: 'XML',
    graphql: 'GraphQL',
  }
  return labels[fileContent.value.language] || fileContent.value.language
})

const lines = computed(() => {
  if (!fileContent.value?.content) return []
  return fileContent.value.content.split('\n')
})

const lineCount = computed(() => lines.value.length)

const gutterWidth = computed(() => {
  const digits = String(lineCount.value).length
  return Math.max(digits, 2)
})

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function fetchContent() {
  loading.value = true
  error.value = null
  fileContent.value = null
  try {
    fileContent.value = await api.get<FileContent>(
      `/projects/${props.projectId}/files/content`,
      { path: props.path, env: props.env },
    )
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Failed to load file'
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.projectId, props.path, props.env],
  fetchContent,
  { immediate: true },
)
</script>

<template>
  <div class="flex flex-col h-full bg-gray-950 rounded-lg border border-gray-800 overflow-hidden">
    <!-- Header bar -->
    <div class="flex items-center gap-3 px-4 py-2 bg-gray-900 border-b border-gray-800 shrink-0">
      <span class="font-mono text-xs text-gray-300 truncate">{{ path }}</span>
      <div class="ml-auto flex items-center gap-3 text-[11px] text-gray-500 shrink-0">
        <span v-if="fileContent" class="flex items-center gap-1">
          <span class="inline-block w-1.5 h-1.5 rounded-full bg-brand-500" />
          {{ languageLabel }}
        </span>
        <span v-if="fileContent">{{ formatSize(fileContent.size) }}</span>
        <span v-if="fileContent">{{ lineCount }} lines</span>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="flex items-center gap-2 text-gray-400 text-sm">
        <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Loading {{ filename }}...
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center px-6">
        <p class="text-red-400 text-sm mb-2">{{ error }}</p>
        <button
          class="text-xs text-brand-400 hover:text-brand-300 underline"
          @click="fetchContent"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- File content with line numbers -->
    <div v-else-if="fileContent" class="flex-1 overflow-auto file-viewer-scroll">
      <table class="file-viewer-table w-full border-collapse">
        <tbody>
          <tr
            v-for="(line, idx) in lines"
            :key="idx"
            class="hover:bg-gray-900/50"
          >
            <td
              class="file-viewer-gutter select-none text-right pr-4 pl-3 text-gray-600 font-mono text-[13px] leading-[22px] align-top border-r border-gray-800/60 bg-gray-950 sticky left-0"
              :style="{ minWidth: `${gutterWidth + 2}ch` }"
            >{{ idx + 1 }}</td>
            <td class="file-viewer-line pl-4 pr-6 font-mono text-[13px] leading-[22px] text-gray-300 whitespace-pre overflow-visible">{{ line }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No content / empty -->
    <div v-else class="flex-1 flex items-center justify-center text-gray-600 text-sm">
      No file selected
    </div>
  </div>
</template>

<style scoped>
.file-viewer-scroll {
  scrollbar-width: thin;
  scrollbar-color: #374151 transparent;
}

.file-viewer-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.file-viewer-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.file-viewer-scroll::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.file-viewer-scroll::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

.file-viewer-table {
  border-spacing: 0;
}

.file-viewer-gutter {
  user-select: none;
  -webkit-user-select: none;
}

.file-viewer-line {
  tab-size: 4;
  -moz-tab-size: 4;
}
</style>
