# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HyprContext is a privacy-focused desktop productivity tracking application for Linux (primarily Hyprland/Wayland). It uses local AI (Ollama) to analyze screen activity and provide productivity insights without sending data to external servers.

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI, ChromaDB for vector storage, Ollama for AI
- **Frontend**: React 18 + TypeScript + Vite, Tailwind CSS, Zustand for state management
- **Desktop**: Electron with system tray integration
- **Packaging**: AppImage for Linux distribution

## Development Commands

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev                    # Vite dev server only
pnpm electron:dev           # Full Electron + Vite development
pnpm build                  # Build for production
pnpm electron:build         # Build AppImage
```

## Architecture

### Backend Structure (`backend/`)
- `main.py` - FastAPI app entry point with background task loops (capture, focus monitoring, system stats)
- `core/config.py` - Pydantic settings with dynamic paths based on user-selected data directory
- `core/dependencies.py` - Dependency injection for services
- `api/routes/` - REST API endpoints: activities, plans, reports, focus, chat, profile, control, config
- `api/websocket/` - Real-time updates for activities, focus status, system stats
- `services/` - Business logic: analyzer, focus tracking, screenshot capture, plans, reports
- `adapters/` - External integrations: Ollama (AI), ChromaDB (vector DB), notifications

### Frontend Structure (`frontend/`)
- `electron/main.cjs` - Electron main process, manages backend lifecycle and system tray
- `src/App.tsx` - React app with HashRouter, first-run setup detection
- `src/pages/` - HomePage, GraphsPage, PlansPage, ReportsPage, SettingsPage, SetupPage
- `src/stores/` - Zustand stores: activity, focus, system
- `src/hooks/` - Custom hooks including `useWebSocket` for real-time updates
- `src/components/glass/` - "Liquid Glass UI" themed components

### Data Flow
1. Electron spawns backend as child process on startup
2. Backend captures screenshots every 30 seconds via `grim`
3. Ollama analyzes screenshots + window context
4. Activities stored in ChromaDB with embeddings for semantic search
5. Frontend receives real-time updates via WebSocket

### Key Configuration
- User data stored at `~/Documents/HyprContext` (configurable)
- Settings persisted at `~/.config/hyprcontext/settings.json`
- Profile information in `profile.yaml` within data directory
- Environment prefix: `HYPRCONTEXT_`

## External Dependencies

- **Ollama**: Required for AI analysis. Models: `gemma3` (analysis), `mxbai-embed-large` (embeddings)
- **grim**: Wayland screenshot utility (Linux)

## API Endpoints

Backend runs on `http://localhost:8000`. Key endpoints:

- `GET /health` - Health check with AI/DB status
- `POST /api/control/start` / `POST /api/control/stop` - Control capture loop
- `GET /api/activities` - Activity history with semantic search
- `WS /ws` - WebSocket for real-time updates

### Reserved Endpoints (Future Features)

The following endpoints are implemented in the backend but not yet used by the frontend:

| Endpoint | Description |
|----------|-------------|
| `GET /api/activities/today` | Get today's activities (frontend uses date param instead) |
| `GET /api/reports/today` | Get today's report |
| `POST /api/focus/reset` | Reset daily distraction warnings |
| `POST /api/chat/stream` | Streaming AI chat response |
| `GET /api/profile/courses` | List education courses |
| `POST /api/profile/courses` | Add new course to profile |
| `DELETE /api/profile/courses/{name}` | Remove course from profile |
| `GET /api/profile/banned-keywords` | Get banned keywords list |
| `PUT /api/profile/banned-keywords` | Update banned keywords |
| `POST /api/control/restart` | Restart capture services |
| `GET /api/config/info` | Debug: get all settings |
