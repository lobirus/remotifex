# Changelog

All notable changes to Remotifex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-02-11

First public release. Phase 1 MVP — the foundation of the self-hosted AI coding platform.

### Added

#### AI Chat Interface
- Chat with Claude Code in real-time from the browser
- Streaming output via WebSocket + Redis pub/sub
- Tool call visibility (file reads, edits, bash commands shown live)
- Model selection per message (Sonnet, Opus, Haiku)
- Session continuity — resume previous conversations
- Custom system prompts and tool allowlists per project

#### Project Management
- Create and manage multiple projects from a single dashboard
- Per-project AI configuration (model, tools, system prompt)
- Project settings page

#### File Browser
- Browse project files directly in the browser
- Syntax highlighting with language detection
- File tree navigation with expandable directories
- Tab-based file viewing

#### Setup & Configuration
- Four-step setup wizard (admin account, AI keys, domain, project domains)
- Global settings panel (AI config, access domain, project domains)
- Encrypted API key storage
- Zero config file editing — everything through the web UI

#### Authentication
- JWT-based authentication
- Admin account creation during setup
- Login page with secure password hashing
- Global auth middleware with setup detection

#### Infrastructure
- Docker Compose orchestration (6 services)
- Caddy reverse proxy with auto-SSL via Let's Encrypt
- One-line installer script
- Dev mode with hot reload (`docker-compose.dev.yml`)
- MongoDB for document storage, Redis for task queue and pub/sub

#### Frontend
- Nuxt 3 + Vue 3 + Tailwind CSS
- Responsive layout (desktop and mobile)
- Pinia stores for auth, projects, and chat state
- Reusable UI component library (buttons, modals, toasts, cards, badges)
- WebSocket composable for live streaming

#### Backend
- FastAPI REST API (~20 endpoints)
- WebSocket endpoint for real-time chat streaming
- Async MongoDB (Motor) and Redis (aioredis)
- Path traversal protection on file operations

#### Worker
- Claude Code CLI subprocess management
- Stream-JSON output parsing
- Token usage tracking per task
- Graceful shutdown handling

### Stats
- 86 files across frontend, backend, worker, and infrastructure
- ~7,400 lines of code

[0.1.0]: https://github.com/lobirus/remotifex/releases/tag/v0.1.0
