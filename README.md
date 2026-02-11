<p align="center">
  <img src="frontend/public/favicon.svg" width="60" alt="Remotifex" />
</p>

<h1 align="center">Remotifex</h1>

<p align="center">
  <strong>Describe it. Build it. Ship it.</strong>
  <br />
  Self-hosted platform where AI writes your code and you ship from anywhere.
</p>

<p align="center">
  <a href="https://remotifex.com" target="_blank">Website</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#features">Features</a> &middot;
  <a href="https://github.com/lobirus/remotifex/issues">Issues</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="License" />
  <img src="https://img.shields.io/badge/self--hosted-yes-green" alt="Self-hosted" />
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome" />
</p>

---

Remotifex is an open-source, self-hosted platform for building software projects with AI. Chat with Claude Code or Amp to write code, preview changes on staging, and deploy to production with one click — all from a web UI that works on desktop and mobile.

Your code, your server, your keys. No vendor lock-in.

## Quick Start

Install on any Linux server with Docker:

```bash
curl -fsSL https://get.remotifex.com | sh
```

Then open `http://your-server-ip` in your browser and complete the setup wizard.

### Requirements

- Linux server (Ubuntu 22.04+ recommended)
- Docker & Docker Compose
- Git
- 2 GB RAM minimum

### Manual Installation

```bash
git clone https://github.com/remotifex/remotifex.git /opt/remotifex
cd /opt/remotifex
cp .env.example .env
# Generate secrets in .env (JWT_SECRET, ENCRYPTION_KEY)
docker compose up -d
# Open http://your-server-ip and complete the setup wizard
```

## Features

### AI-Powered Development
- **Chat-driven coding** — describe what you want in plain language, AI writes the code
- **Claude Code & Amp** — choose your preferred AI tool per project
- **Streaming output** — watch the AI work in real-time with tool call visibility
- **Session continuity** — pick up where you left off with conversation history

### Project Management
- **Multi-project** — manage unlimited projects from a single dashboard
- **File browser** — browse and view project files directly in the browser
- **Custom Dockerfiles** — use any tech stack (Node, Python, Go, Rust, etc.)

### Environments & Deployment
- **Auto staging/production** — every project gets both environments automatically
- **One-click deploy** — push staging to production when ready
- **Instant rollback** — revert to any previous deployment
- **Environment variables** — per-environment secret management

### Infrastructure
- **Auto SSL** — HTTPS certificates handled automatically via Caddy
- **Custom domains** — connect your own domain to any project
- **Git integration** — link GitHub/GitLab repos, commit and push from the UI

### Access & Collaboration
- **Multi-user** — invite team members with username/password auth
- **Mobile-friendly** — full functionality from your phone
- **Access from anywhere** — it's a web app on your server

## Architecture

```
Browser / Mobile
       |
    [ Caddy ]  ── auto SSL, routing ──
       |                    |
  [ Frontend ]        [ Backend API ]
    Nuxt 3              FastAPI
       |                    |
       |         ┌──────────┼──────────┐
       |         |          |          |
       |     [ MongoDB ]  [ Redis ] [ Worker ]
       |                              Claude Code / Amp
       |                                   |
       └───────────────────────────────────┘
```

| Service | Technology | Purpose |
|---------|-----------|---------|
| **Frontend** | Nuxt 3, Vue 3, Tailwind | Web UI |
| **Backend** | Python, FastAPI | REST API, WebSocket |
| **Worker** | Python, Claude Code CLI | AI task execution |
| **Database** | MongoDB 7 | Document storage |
| **Queue** | Redis 7 | Task queue, pub/sub streaming |
| **Proxy** | Caddy | Reverse proxy, auto SSL |

## Configuration

All configuration is done via the web UI — no manual file editing required. The setup wizard walks you through:

1. **Admin account** — create your first user
2. **AI keys** — connect Claude Code (and optionally Amp)
3. **Access** — optionally configure a custom domain for Remotifex

After setup, go to **Settings** to manage:
- AI configuration
- Remotifex access (custom domain, port)
- Project domains (base domain for staging/production environments)
- SSL certificates (via Let's Encrypt)

The `.env` file only contains auto-generated secrets and service URLs. You should never need to edit it manually.

### Setting Up a Domain

1. Open **Settings > Remotifex Access** in the web UI
2. Enter your domain — the UI shows DNS instructions (A record → your server IP)
3. Save — Caddy automatically provisions an SSL certificate

For project subdomains (e.g., `myapp.projects.example.com`):
1. Open **Settings > Project Domains**
2. Enter a base domain and set up a wildcard DNS record as shown

## Development

### Prerequisites

- Node.js 22+
- Python 3.12+
- Docker & Docker Compose
- MongoDB (or use Docker)
- Redis (or use Docker)

### Running Locally

```bash
# Start infrastructure services
docker compose -f docker-compose.yml -f docker-compose.dev.yml up mongo redis -d

# Backend
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Worker (optional — needed for AI chat)
cd worker
pip install -e .
python -m app.main
```

The frontend runs at `http://localhost:3000` with API proxied to `http://localhost:8000`.

### Project Structure

```
remotifex/
├── frontend/          # Nuxt 3 + Vue 3 + Tailwind
├── backend/           # FastAPI REST API + WebSocket
├── worker/            # AI task runner (Claude Code / Amp)
├── caddy/             # Reverse proxy config
├── docker-compose.yml # Production orchestration
├── docker-compose.dev.yml
├── install.sh         # One-line installer
└── .env.example       # Configuration template
```

## Updating

```bash
cd /opt/remotifex
git pull
docker compose up -d --build
```

## Roadmap

- [x] **Phase 1** — AI chat, file browser, setup wizard, auth
- [ ] **Phase 2** — Monaco editor, environment variables, container management
- [ ] **Phase 3** — Deploy/rollback workflow, Git integration
- [ ] **Phase 4** — Multi-user management, email providers
- [ ] **Phase 5** — REST API, MCP server, Amp support, mobile polish

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For bugs and feature requests, please [open an issue](https://github.com/remotifex/remotifex/issues).

## Security

If you discover a security vulnerability, please email security@remotifex.com instead of opening a public issue.

## License

Remotifex is open-source software licensed under the [GNU Affero General Public License v3.0](LICENSE).

This means you can freely use, modify, and distribute Remotifex, but any modified version that's accessible over a network must also be open-sourced under AGPL-3.0.

---

<p align="center">
  Built by <a href="https://lobirus.com/">Bálint Horváth (lobirus)</a>
</p>
