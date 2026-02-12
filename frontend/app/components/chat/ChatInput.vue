<script setup lang="ts">
const emit = defineEmits<{
  send: [content: string]
}>()

const chatStore = useChatStore()

const content = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => {
  return content.value.trim().length > 0 && !chatStore.isStreaming
})

function adjustHeight() {
  const textarea = textareaRef.value
  if (!textarea) return

  // Reset height to auto to get correct scrollHeight
  textarea.style.height = 'auto'

  // Calculate new height (min 1 line ~40px, max 6 lines ~168px)
  const lineHeight = 24
  const padding = 16
  const minHeight = lineHeight + padding
  const maxHeight = lineHeight * 6 + padding

  const newHeight = Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)
  textarea.style.height = `${newHeight}px`
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    send()
  }
}

function send() {
  const trimmed = content.value.trim()
  if (!trimmed || chatStore.isStreaming) return

  emit('send', trimmed)
  content.value = ''

  // Reset textarea height after clearing
  nextTick(() => {
    adjustHeight()
  })
}

watch(content, () => {
  nextTick(() => {
    adjustHeight()
  })
})

onMounted(() => {
  adjustHeight()
})
</script>

<template>
  <div class="border-t border-edge bg-surface p-4">
    <div class="flex items-end gap-2 max-w-3xl mx-auto">
      <!-- Textarea -->
      <div class="relative flex-1">
        <textarea
          ref="textareaRef"
          v-model="content"
          :disabled="chatStore.isStreaming"
          placeholder="Ask Claude to make changes..."
          rows="1"
          class="w-full resize-none rounded-xl border border-edge bg-surface px-4 py-2.5 text-sm text-heading placeholder-faint focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none disabled:bg-inset disabled:text-faint disabled:cursor-not-allowed transition-colors"
          @keydown="handleKeydown"
        />
      </div>

      <!-- Send button -->
      <button
        :disabled="!canSend"
        class="flex items-center justify-center w-10 h-10 rounded-xl bg-brand-600 text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:bg-surface-active disabled:text-faint disabled:cursor-not-allowed transition-colors shrink-0"
        @click="send"
      >
        <!-- Send arrow icon -->
        <svg
          class="w-5 h-5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M3.105 2.288a.75.75 0 00-.826.95l1.414 4.926A1.5 1.5 0 005.135 9.25h6.115a.75.75 0 010 1.5H5.135a1.5 1.5 0 00-1.442 1.086l-1.414 4.926a.75.75 0 00.826.95 28.11 28.11 0 0015.293-7.154.75.75 0 000-1.115A28.11 28.11 0 003.105 2.289z"
          />
        </svg>
      </button>
    </div>

    <!-- Streaming indicator -->
    <div
      v-if="chatStore.isStreaming"
      class="flex items-center justify-center gap-2 mt-2 text-xs text-faint"
    >
      <svg
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
      Claude is working...
    </div>
  </div>
</template>
