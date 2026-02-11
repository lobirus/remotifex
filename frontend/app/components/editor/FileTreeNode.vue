<script setup lang="ts">
import type { FileEntry } from '~/types'

interface TreeNode {
  entry: FileEntry
  path: string
  expanded: boolean
  loading: boolean
  children: TreeNode[]
  loaded: boolean
}

interface Props {
  node: TreeNode
  depth: number
}

const props = defineProps<Props>()

const toggleNode = inject<(node: TreeNode) => void>('fileTree:toggleNode')!
const getFileIcon = inject<(name: string) => { symbol: string; color: string }>('fileTree:getFileIcon')!
const formatSize = inject<(bytes: number) => string>('fileTree:formatSize')!
const selectedPath = inject<Ref<string | null>>('fileTree:selectedPath')!

const isDir = computed(() => props.node.entry.type === 'directory')
const isSelected = computed(() => selectedPath.value === props.node.path)
const icon = computed(() => getFileIcon(props.node.entry.name))
const indentPx = computed(() => `${props.depth * 16 + 8}px`)
</script>

<template>
  <div>
    <!-- Row -->
    <div
      class="flex items-center py-1 pr-2 cursor-pointer rounded-sm group"
      :class="[
        isSelected ? 'bg-brand-900/40 text-brand-200' : 'text-gray-300 hover:bg-gray-800/60',
      ]"
      :style="{ paddingLeft: indentPx }"
      @click="toggleNode(node)"
    >
      <!-- Chevron for directories -->
      <span
        v-if="isDir"
        class="inline-flex items-center justify-center w-3 text-gray-500 text-[10px] transition-transform duration-150 mr-1"
        :class="{ 'rotate-90': node.expanded }"
      >&#9654;</span>
      <span v-else class="inline-block w-3 mr-1" />

      <!-- Icon -->
      <span v-if="isDir" class="text-xs mr-1.5 shrink-0">
        {{ node.expanded ? '\uD83D\uDCC2' : '\uD83D\uDCC1' }}
      </span>
      <span
        v-else
        class="font-mono text-[9px] font-bold leading-none mr-1.5 w-4 text-center inline-block shrink-0"
        :class="icon.color"
      >{{ icon.symbol }}</span>

      <!-- Name -->
      <span class="truncate">{{ node.entry.name }}</span>

      <!-- Loading spinner for directory -->
      <svg
        v-if="node.loading"
        class="animate-spin h-3 w-3 ml-auto shrink-0 text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>

      <!-- File size -->
      <span
        v-if="!isDir && !node.loading"
        class="ml-auto pl-2 text-[10px] text-gray-600 shrink-0"
      >{{ formatSize(node.entry.size) }}</span>
    </div>

    <!-- Children (recursive) -->
    <ul v-if="isDir && node.expanded && node.children.length > 0" class="space-y-px">
      <li v-for="child in node.children" :key="child.path">
        <FileTreeNode :node="child" :depth="depth + 1" />
      </li>
    </ul>
  </div>
</template>
