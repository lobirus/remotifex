import type { StreamEvent } from '~/types'

/**
 * WebSocket composable for real-time chat streaming.
 * Connects to the backend WebSocket endpoint and processes streaming events.
 */
export function useWebSocket(projectId: Ref<string> | string) {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const chatStore = useChatStore()

  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 10

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) return

    const id = toValue(projectId)
    const token = authStore.token
    if (!token || !id) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}${config.public.wsUrl}/chat/${id}?token=${token}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      connected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onclose = () => {
      connected.value = false
      scheduleReconnect()
    }

    ws.value.onerror = () => {
      connected.value = false
    }

    ws.value.onmessage = (event) => {
      try {
        const data: StreamEvent = JSON.parse(event.data)
        chatStore.processStreamEvent(data)
      } catch {
        // Ignore malformed messages
      }
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  function scheduleReconnect() {
    if (reconnectAttempts.value >= maxReconnectAttempts) return

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
    reconnectAttempts.value++

    reconnectTimer = setTimeout(() => {
      connect()
    }, delay)
  }

  // Auto-connect on mount, disconnect on unmount
  if (import.meta.client) {
    onMounted(() => connect())
    onUnmounted(() => disconnect())
  }

  return {
    connected,
    connect,
    disconnect,
  }
}
