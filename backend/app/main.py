"""Remotifex API server."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongodb import close_db, connect_db
from app.routers import auth, chat, files, projects, settings, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: connect/disconnect database."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Remotifex API",
    version="0.1.0",
    description="AI-powered remote software development platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes under /api prefix (Caddy forwards /api/* with path intact)
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(
    chat.router, prefix="/projects/{project_id}/chat", tags=["chat"]
)
api_router.include_router(
    files.router, prefix="/projects/{project_id}/files", tags=["files"]
)
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
app.include_router(api_router)

# WebSocket routes under /ws prefix (Caddy forwards /ws/* with path intact)
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
