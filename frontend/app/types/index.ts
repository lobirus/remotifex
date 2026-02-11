// User types
export interface User {
  id: string
  username: string
  is_admin: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// Project types
export interface Project {
  id: string
  name: string
  slug: string
  description: string
  owner_id: string
  status: string
  ai_config: AIConfig
  git: GitConfig
  created_at: string
  updated_at: string
}

export interface AIConfig {
  tool: 'claude' | 'amp'
  model: string
  allowed_tools: string[]
  append_system_prompt: string | null
}

export interface GitConfig {
  repo_url: string | null
  branch: string
  credentials: {
    type: string
    token_encrypted: string
  } | null
}

// Chat types
export interface ChatSession {
  id: string
  project_id: string
  title: string
  status: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  project_id: string
  role: 'user' | 'assistant'
  content: string
  tool_calls: ToolCall[]
  metadata: Record<string, unknown>
  created_at: string
  isStreaming?: boolean
}

export interface ToolCall {
  tool: string
  input: Record<string, unknown>
  output_summary: string
  status: string
}

export interface ChatSendResponse {
  task_id: string
  message_id: string
  session_id: string
}

// Stream event types
export interface StreamEvent {
  task_id: string
  event: {
    type: string
    content?: string
    tool?: string
    id?: string
    return_code?: number
    session_id?: string
    error?: string
    stop_reason?: string
    usage?: Record<string, number>
    cost_usd?: number
    duration_ms?: number
    num_turns?: number
  }
}

// File browser types
export interface FileEntry {
  name: string
  type: 'file' | 'directory'
  size: number
  modified: string
}

export interface FileContent {
  path: string
  content: string
  language: string | null
  size: number
}

// Settings types
export interface SetupStatus {
  setup_completed: boolean
}

export interface AppSettings {
  type: string
  setup_completed: boolean
  ai: {
    default_tool: string
    claude_api_key_set: boolean
    claude_default_model: string
    amp_api_key_set: boolean
  }
  email: {
    provider: string | null
  }
  domain: {
    base_domain: string | null
    ssl_email: string | null
  }
  access: {
    remotifex_domain: string | null
    port: number
  }
  api: {
    enabled: boolean
  }
  mcp: {
    enabled: boolean
  }
}

export interface ServerInfo {
  ip: string | null
  port: number
  remotifex_domain: string | null
  current_url: string
}
