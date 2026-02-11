<script setup lang="ts">
import { marked } from 'marked'
import type { ChatMessage } from '~/types'

interface Props {
  message: ChatMessage
}

const props = defineProps<Props>()

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')

// Configure marked for safe rendering
marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked.parse(props.message.content) as string
})

const formattedTime = computed(() => {
  if (!props.message.created_at) return ''
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
})

const hasToolCalls = computed(() => {
  return props.message.tool_calls && props.message.tool_calls.length > 0
})
</script>

<template>
  <div
    class="flex gap-3 animate-fade-in"
    :class="isUser ? 'flex-row-reverse' : 'flex-row'"
  >
    <!-- Avatar -->
    <div
      class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold"
      :class="isUser
        ? 'bg-brand-600 text-white'
        : 'bg-gray-200 text-gray-600'"
    >
      <template v-if="isUser">U</template>
      <template v-else>
        <!-- Sparkle icon for assistant -->
        <svg
          class="w-4 h-4"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M10.868 2.884c-.321-.772-1.415-.772-1.736 0l-1.83 4.401-4.753.381c-.833.067-1.171 1.107-.536 1.651l3.62 3.102-1.106 4.637c-.194.813.691 1.456 1.405 1.02L10 15.591l4.069 2.485c.713.436 1.598-.207 1.404-1.02l-1.106-4.637 3.62-3.102c.635-.544.297-1.584-.536-1.65l-4.752-.382-1.831-4.401z"
          />
        </svg>
      </template>
    </div>

    <!-- Message bubble -->
    <div
      class="max-w-[80%] min-w-0"
      :class="isUser ? 'items-end' : 'items-start'"
    >
      <div
        class="rounded-2xl px-4 py-3"
        :class="isUser
          ? 'bg-brand-600 text-white rounded-br-md'
          : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'"
      >
        <!-- Message content as rendered markdown -->
        <div
          v-if="message.content"
          class="prose prose-sm max-w-none break-words"
          :class="isUser
            ? 'prose-invert prose-p:text-white prose-headings:text-white prose-strong:text-white prose-code:text-white/90 prose-a:text-white prose-a:underline'
            : 'prose-gray'"
          v-html="renderedContent"
        />

        <!-- Tool calls -->
        <div v-if="hasToolCalls && isAssistant">
          <ToolCallBlock
            v-for="(toolCall, index) in message.tool_calls"
            :key="index"
            :tool-call="toolCall"
          />
        </div>

        <!-- Streaming cursor -->
        <StreamingCursor v-if="message.isStreaming" />
      </div>

      <!-- Timestamp -->
      <p
        class="mt-1 text-xs text-gray-400 px-1"
        :class="isUser ? 'text-right' : 'text-left'"
      >
        {{ formattedTime }}
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Ensure code blocks inside markdown look clean */
:deep(pre) {
  @apply rounded-lg text-sm overflow-x-auto;
}

:deep(code) {
  @apply text-sm;
}

:deep(pre code) {
  @apply bg-transparent p-0;
}

:deep(p:last-child) {
  @apply mb-0;
}

:deep(p:first-child) {
  @apply mt-0;
}

:deep(ul), :deep(ol) {
  @apply my-1;
}
</style>
