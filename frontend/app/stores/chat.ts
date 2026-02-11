import type { ChatMessage, ChatSendResponse, ChatSession, StreamEvent } from '~/types'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const messages = ref<ChatMessage[]>([])
  const currentSessionId = ref<string | null>(null)
  const activeTaskId = ref<string | null>(null)
  const isStreaming = ref(false)
  const loading = ref(false)

  async function fetchSessions(projectId: string) {
    const api = useApi()
    sessions.value = await api.get<ChatSession[]>(`/projects/${projectId}/chat/sessions`)
  }

  async function fetchMessages(projectId: string, sessionId?: string) {
    const api = useApi()
    const query: Record<string, string> = {}
    if (sessionId) query.session_id = sessionId
    messages.value = await api.get<ChatMessage[]>(
      `/projects/${projectId}/chat/messages`,
      query,
    )
  }

  async function sendMessage(projectId: string, content: string): Promise<ChatSendResponse> {
    const api = useApi()

    // Optimistic: add user message locally
    const tempId = `temp-${Date.now()}`
    messages.value.push({
      id: tempId,
      session_id: currentSessionId.value || '',
      project_id: projectId,
      role: 'user',
      content,
      tool_calls: [],
      metadata: {},
      created_at: new Date().toISOString(),
    })

    const body: { content: string; session_id?: string } = { content }
    if (currentSessionId.value) {
      body.session_id = currentSessionId.value
    }

    const response = await api.post<ChatSendResponse>(
      `/projects/${projectId}/chat/messages`,
      body,
    )

    // Update session ID
    currentSessionId.value = response.session_id
    activeTaskId.value = response.task_id
    isStreaming.value = true

    // Add placeholder for assistant response
    messages.value.push({
      id: `assistant-${response.task_id}`,
      session_id: response.session_id,
      project_id: projectId,
      role: 'assistant',
      content: '',
      tool_calls: [],
      metadata: {},
      created_at: new Date().toISOString(),
      isStreaming: true,
    })

    return response
  }

  function processStreamEvent(event: StreamEvent) {
    if (event.task_id !== activeTaskId.value) return

    const lastMsg = messages.value[messages.value.length - 1]
    if (!lastMsg || lastMsg.role !== 'assistant') return

    switch (event.event.type) {
      case 'text':
        lastMsg.content += event.event.content || ''
        break

      case 'tool_use_start':
        lastMsg.tool_calls.push({
          tool: event.event.tool || 'unknown',
          input: {},
          output_summary: '',
          status: 'running',
        })
        break

      case 'task_complete':
        lastMsg.isStreaming = false
        isStreaming.value = false
        activeTaskId.value = null
        break

      case 'task_error':
        lastMsg.isStreaming = false
        lastMsg.content += `\n\nError: ${event.event.error}`
        isStreaming.value = false
        activeTaskId.value = null
        break

      case 'result':
        lastMsg.metadata = {
          ...lastMsg.metadata,
          cost_usd: event.event.cost_usd,
          duration_ms: event.event.duration_ms,
          num_turns: event.event.num_turns,
        }
        break
    }
  }

  function clearMessages() {
    messages.value = []
    currentSessionId.value = null
    activeTaskId.value = null
    isStreaming.value = false
  }

  return {
    sessions,
    messages,
    currentSessionId,
    activeTaskId,
    isStreaming,
    loading,
    fetchSessions,
    fetchMessages,
    sendMessage,
    processStreamEvent,
    clearMessages,
  }
})
