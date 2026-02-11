<script setup lang="ts">
interface Tab {
  path: string
  active: boolean
}

interface Props {
  tabs: Tab[]
}

defineProps<Props>()

const emit = defineEmits<{
  select: [path: string]
  close: [path: string]
}>()

function getFilename(path: string): string {
  const parts = path.split('/')
  return parts[parts.length - 1] || path
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
    sh: { symbol: '$', color: 'text-green-300' },
    rs: { symbol: 'Rs', color: 'text-orange-500' },
    go: { symbol: 'Go', color: 'text-cyan-400' },
  }
  return map[ext] || { symbol: '~~', color: 'text-gray-400' }
}

function onClose(event: MouseEvent, path: string) {
  event.stopPropagation()
  emit('close', path)
}
</script>

<template>
  <div
    v-if="tabs.length > 0"
    class="flex items-end bg-gray-900 border-b border-gray-800 overflow-x-auto editor-tabs-scroll"
  >
    <div class="flex items-end min-w-0">
      <button
        v-for="tab in tabs"
        :key="tab.path"
        class="group relative flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-r border-gray-800/50 shrink-0 max-w-[180px] transition-colors duration-100"
        :class="[
          tab.active
            ? 'bg-gray-950 text-gray-200'
            : 'bg-gray-900 text-gray-500 hover:text-gray-300 hover:bg-gray-850',
        ]"
        :title="tab.path"
        @click="emit('select', tab.path)"
      >
        <!-- Active indicator - bottom border -->
        <span
          v-if="tab.active"
          class="absolute bottom-0 left-0 right-0 h-[2px] bg-brand-500"
        />

        <!-- File type icon -->
        <span
          class="font-mono text-[9px] font-bold leading-none shrink-0"
          :class="getFileIcon(getFilename(tab.path)).color"
        >{{ getFileIcon(getFilename(tab.path)).symbol }}</span>

        <!-- Filename -->
        <span class="truncate">{{ getFilename(tab.path) }}</span>

        <!-- Close button -->
        <span
          class="inline-flex items-center justify-center w-4 h-4 ml-1 rounded-sm shrink-0 opacity-0 group-hover:opacity-100 hover:bg-gray-700 transition-opacity duration-100"
          :class="{ 'opacity-60': tab.active }"
          @click="onClose($event, tab.path)"
        >&times;</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.editor-tabs-scroll {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.editor-tabs-scroll::-webkit-scrollbar {
  display: none;
}
</style>
