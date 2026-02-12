<script setup lang="ts">
interface Props {
  projectId: string
}

const props = defineProps<Props>()

const chatStore = useChatStore()
const { connected } = useWebSocket(props.projectId)

const messagesContainer = ref<HTMLDivElement | null>(null)
const isNearBottom = ref(true)

// Load existing messages on mount
onMounted(async () => {
  await chatStore.fetchMessages(props.projectId)
  scrollToBottom()
})

// Auto-scroll on new messages when user is near the bottom
watch(
  () => chatStore.messages.length,
  () => {
    if (isNearBottom.value) {
      nextTick(() => scrollToBottom())
    }
  },
)

// Also auto-scroll when streaming content updates
watch(
  () => {
    const last = chatStore.messages[chatStore.messages.length - 1]
    return last?.content?.length ?? 0
  },
  () => {
    if (isNearBottom.value) {
      nextTick(() => scrollToBottom())
    }
  },
)

function scrollToBottom() {
  const container = messagesContainer.value
  if (!container) return
  container.scrollTop = container.scrollHeight
}

function handleScroll() {
  const container = messagesContainer.value
  if (!container) return

  // Consider "near bottom" if within 100px of the bottom
  const threshold = 100
  isNearBottom.value =
    container.scrollHeight - container.scrollTop - container.clientHeight < threshold
}

async function handleSend(content: string) {
  await chatStore.sendMessage(props.projectId, content)
  nextTick(() => scrollToBottom())
}

function startNewConversation() {
  chatStore.clearMessages()
}

const currentSession = computed(() => {
  if (!chatStore.currentSessionId) return null
  return chatStore.sessions.find((s) => s.id === chatStore.currentSessionId) ?? null
})

const hasMessages = computed(() => chatStore.messages.length > 0)
</script>

<template>
  <div class="flex flex-col h-full bg-inset">
    <!-- Top bar: session info + controls -->
    <div class="flex items-center justify-between border-b border-edge bg-surface px-4 py-3">
      <div class="flex items-center gap-3 min-w-0">
        <h2 class="text-sm font-semibold text-heading truncate">
          {{ currentSession?.title || 'New conversation' }}
        </h2>

        <!-- Connection indicator -->
        <span
          class="inline-flex items-center gap-1 text-xs"
          :class="connected ? 'text-green-600' : 'text-faint'"
        >
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="connected ? 'bg-green-500' : 'bg-faint'"
          />
          {{ connected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>

      <button
        class="btn-secondary btn-sm"
        @click="startNewConversation"
      >
        <svg
          class="w-3.5 h-3.5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"
          />
        </svg>
        New conversation
      </button>
    </div>

    <!-- Message list (scrollable middle area) -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto"
      @scroll="handleScroll"
    >
      <!-- Empty state -->
      <div
        v-if="!hasMessages"
        class="flex flex-col items-center justify-center h-full text-center px-4"
      >
        <div class="w-16 h-16 rounded-full bg-brand-soft flex items-center justify-center mb-4">
          <svg
            class="w-8 h-8 text-brand-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              d="M4.913 2.658c2.075-.27 4.19-.408 6.337-.408 2.147 0 4.262.139 6.337.408 1.922.25 3.291 1.861 3.405 3.727a4.403 4.403 0 00-1.032-.211 50.89 50.89 0 00-8.42 0c-2.358.196-4.04 2.19-4.04 4.434v4.286a4.47 4.47 0 002.433 3.984L7.28 21.53A.75.75 0 016 21v-4.03a48.527 48.527 0 01-1.087-.128C2.905 16.58 1.5 14.833 1.5 12.862V6.638c0-1.97 1.405-3.718 3.413-3.979z"
            />
            <path
              d="M15.75 7.5c-1.376 0-2.739.057-4.086.169C10.124 7.797 9 9.103 9 10.609v4.285c0 1.507 1.128 2.814 2.67 2.94 1.243.102 2.5.157 3.768.165l2.782 2.781a.75.75 0 001.28-.53v-2.39l.33-.026c1.542-.125 2.67-1.433 2.67-2.94v-4.286c0-1.505-1.125-2.811-2.664-2.94A49.392 49.392 0 0015.75 7.5z"
            />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-heading mb-1">Start a conversation</h3>
        <p class="text-sm text-muted max-w-sm">
          Ask Claude to write code, fix bugs, refactor, or make any changes to your project.
        </p>
      </div>

      <!-- Messages -->
      <div v-else class="max-w-3xl mx-auto px-4 py-6 space-y-6">
        <ChatMessage
          v-for="message in chatStore.messages"
          :key="message.id"
          :message="message"
        />
      </div>
    </div>

    <!-- Input area (bottom) -->
    <ChatInput @send="handleSend" />
  </div>
</template>
