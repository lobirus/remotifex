<script setup lang="ts">
import type { FileEntry } from '~/types'

interface Props {
  projectId: string
  env?: string
}

const props = withDefaults(defineProps<Props>(), {
  env: 'staging',
})

const emit = defineEmits<{
  select: [path: string]
}>()

const api = useApi()

interface TreeNode {
  entry: FileEntry
  path: string
  expanded: boolean
  loading: boolean
  children: TreeNode[]
  loaded: boolean
}

const rootNodes = ref<TreeNode[]>([])
const rootLoading = ref(true)
const rootError = ref<string | null>(null)
const selectedPath = ref<string | null>(null)

async function fetchDirectory(path: string): Promise<TreeNode[]> {
  const entries = await api.get<FileEntry[]>(
    `/projects/${props.projectId}/files/list`,
    { path, env: props.env },
  )

  const sorted = [...entries].sort((a, b) => {
    if (a.type !== b.type) return a.type === 'directory' ? -1 : 1
    return a.name.localeCompare(b.name)
  })

  return sorted.map((entry) => ({
    entry,
    path: path ? `${path}/${entry.name}` : entry.name,
    expanded: false,
    loading: false,
    children: [],
    loaded: false,
  }))
}

async function loadRoot() {
  rootLoading.value = true
  rootError.value = null
  try {
    rootNodes.value = await fetchDirectory('')
  } catch (err: unknown) {
    rootError.value = err instanceof Error ? err.message : 'Failed to load files'
  } finally {
    rootLoading.value = false
  }
}

async function toggleNode(node: TreeNode) {
  if (node.entry.type === 'file') {
    selectedPath.value = node.path
    emit('select', node.path)
    return
  }

  if (node.expanded) {
    node.expanded = false
    return
  }

  if (!node.loaded) {
    node.loading = true
    try {
      node.children = await fetchDirectory(node.path)
      node.loaded = true
    } catch {
      node.children = []
    } finally {
      node.loading = false
    }
  }

  node.expanded = true
}

function getFileIcon(name: string): { symbol: string; color: string } {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  const map: Record<string, { symbol: string; color: string }> = {
    ts: { symbol: 'TS', color: 'text-blue-400' },
    tsx: { symbol: 'TX', color: 'text-blue-300' },
    js: { symbol: 'JS', color: 'text-yellow-400' },
    jsx: { symbol: 'JX', color: 'text-yellow-300' },
    vue: { symbol: 'V', color: 'text-green-400' },
    py: { symbol: 'Py', color: 'text-yellow-500' },
    json: { symbol: '{}', color: 'text-amber-400' },
    md: { symbol: 'M', color: 'text-gray-400' },
    css: { symbol: '#', color: 'text-purple-400' },
    scss: { symbol: '#', color: 'text-pink-400' },
    html: { symbol: '<>', color: 'text-orange-400' },
    yaml: { symbol: 'Y', color: 'text-red-300' },
    yml: { symbol: 'Y', color: 'text-red-300' },
    toml: { symbol: 'T', color: 'text-orange-300' },
    sh: { symbol: '$', color: 'text-green-300' },
    bash: { symbol: '$', color: 'text-green-300' },
    rs: { symbol: 'Rs', color: 'text-orange-500' },
    go: { symbol: 'Go', color: 'text-cyan-400' },
    rb: { symbol: 'Rb', color: 'text-red-400' },
    svg: { symbol: 'Sv', color: 'text-orange-300' },
    png: { symbol: 'Im', color: 'text-pink-300' },
    jpg: { symbol: 'Im', color: 'text-pink-300' },
    gif: { symbol: 'Im', color: 'text-pink-300' },
    lock: { symbol: 'Lk', color: 'text-gray-500' },
    env: { symbol: 'Ev', color: 'text-yellow-600' },
    sql: { symbol: 'Sq', color: 'text-blue-300' },
    txt: { symbol: 'Tx', color: 'text-gray-400' },
  }
  return map[ext] || { symbol: '~~', color: 'text-gray-400' }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

provide('fileTree:toggleNode', toggleNode)
provide('fileTree:getFileIcon', getFileIcon)
provide('fileTree:formatSize', formatSize)
provide('fileTree:selectedPath', selectedPath)

onMounted(loadRoot)

watch(() => [props.projectId, props.env], loadRoot)
</script>

<template>
  <div class="text-sm select-none">
    <!-- Loading state -->
    <div v-if="rootLoading" class="px-3 py-4 text-gray-400 text-xs">
      <div class="flex items-center gap-2">
        <svg class="animate-spin h-3.5 w-3.5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Loading files...
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="rootError" class="px-3 py-4">
      <p class="text-red-400 text-xs mb-2">{{ rootError }}</p>
      <button
        class="text-xs text-brand-400 hover:text-brand-300 underline"
        @click="loadRoot"
      >
        Retry
      </button>
    </div>

    <!-- Empty state -->
    <div v-else-if="rootNodes.length === 0" class="px-3 py-4 text-gray-500 text-xs">
      No files found.
    </div>

    <!-- File tree -->
    <ul v-else class="space-y-px">
      <li v-for="node in rootNodes" :key="node.path">
        <FileTreeNode :node="node" :depth="0" />
      </li>
    </ul>
  </div>
</template>
