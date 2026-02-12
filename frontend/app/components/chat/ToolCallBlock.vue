<script setup lang="ts">
import type { ToolCall } from '~/types'

interface Props {
  toolCall: ToolCall
}

const props = defineProps<Props>()

const expanded = ref(false)

const isRunning = computed(() => props.toolCall.status === 'running')

const statusLabel = computed(() => {
  switch (props.toolCall.status) {
    case 'running':
      return 'Running'
    case 'completed':
      return 'Completed'
    case 'error':
      return 'Error'
    default:
      return props.toolCall.status
  }
})

const statusClass = computed(() => {
  switch (props.toolCall.status) {
    case 'running':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    case 'completed':
      return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
    case 'error':
      return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
    default:
      return 'bg-surface-hover text-muted'
  }
})

const formattedInput = computed(() => {
  if (!props.toolCall.input || Object.keys(props.toolCall.input).length === 0) {
    return null
  }
  try {
    return JSON.stringify(props.toolCall.input, null, 2)
  } catch {
    return String(props.toolCall.input)
  }
})

function toggle() {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="my-2 rounded-lg border border-edge bg-inset overflow-hidden">
    <!-- Header -->
    <button
      class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-surface-hover transition-colors"
      @click="toggle"
    >
      <!-- Chevron -->
      <svg
        class="w-4 h-4 text-faint shrink-0 transition-transform duration-200"
        :class="{ 'rotate-90': expanded }"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
          clip-rule="evenodd"
        />
      </svg>

      <!-- Tool icon -->
      <svg
        class="w-4 h-4 text-muted shrink-0"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M14.5 10a4.5 4.5 0 004.284-5.882c-.105-.324-.51-.391-.752-.15L15.34 6.66a.454.454 0 01-.493.11 3.01 3.01 0 01-1.618-1.616.455.455 0 01.11-.494l2.694-2.692c.24-.241.174-.647-.15-.752a4.5 4.5 0 00-5.873 4.575c.055.873-.128 1.808-.8 2.368l-7.23 6.024a2.724 2.724 0 103.837 3.837l6.024-7.23c.56-.672 1.495-.855 2.368-.8.096.007.193.01.291.01zM5 16a1 1 0 11-2 0 1 1 0 012 0z"
          clip-rule="evenodd"
        />
      </svg>

      <!-- Tool name -->
      <span class="text-sm font-medium text-sub truncate">
        {{ toolCall.tool }}
      </span>

      <!-- Status badge -->
      <span
        class="ml-auto inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium shrink-0"
        :class="statusClass"
      >
        <!-- Spinner for running status -->
        <svg
          v-if="isRunning"
          class="w-3 h-3 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        {{ statusLabel }}
      </span>
    </button>

    <!-- Expanded content -->
    <div v-if="expanded" class="border-t border-edge px-3 py-2 space-y-2">
      <!-- Input -->
      <div v-if="formattedInput">
        <p class="text-xs font-medium text-muted uppercase tracking-wide mb-1">Input</p>
        <pre class="text-xs font-mono text-sub bg-surface rounded border border-edge p-2 overflow-x-auto whitespace-pre-wrap break-words">{{ formattedInput }}</pre>
      </div>

      <!-- Output -->
      <div v-if="toolCall.output_summary">
        <p class="text-xs font-medium text-muted uppercase tracking-wide mb-1">Output</p>
        <pre class="text-xs font-mono text-sub bg-surface rounded border border-edge p-2 overflow-x-auto whitespace-pre-wrap break-words">{{ toolCall.output_summary }}</pre>
      </div>

      <!-- Empty state -->
      <p
        v-if="!formattedInput && !toolCall.output_summary"
        class="text-xs text-faint italic"
      >
        No details available.
      </p>
    </div>
  </div>
</template>
