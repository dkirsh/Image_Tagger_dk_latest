# Image Tagger v3 — Frontend Setup Guide

## Architecture

The frontend is a **Vite + React monorepo** with 4 independent apps sharing
common components. Each app runs on its own port and proxies `/api` requests
to the FastAPI backend.

```
frontend/
├── shared/                  # Shared components (Header, Button, Toast, ApiClient)
├── apps/
│   ├── explorer/   :3004    # Image browse/search with debug overlays
│   ├── workbench/  :3001    # HITL tagger annotation interface
│   ├── admin/      :3003    # Upload, VLM config, science runs, cost dashboard
│   └── monitor/    :3002    # System health, velocity, inter-rater reliability
├── package.json             # Root workspace
└── vite.config.base.js      # Shared Vite config (proxy, aliases, build)
```

## Prerequisites

1. **Node.js 18+** (check with `node --version`)
2. **PostgreSQL** running with a database `image_tagger_v3`
3. **Python 3.11+** with the backend venv set up

## Quick Start

### 1. Set up the database

```bash
# Create the database (if not already created)
createdb image_tagger_v3

# Or with custom credentials:
psql -c "CREATE DATABASE image_tagger_v3;"
```

### 2. Start the backend

```bash
cd TRS_v1.1/backend

# Set database URL (adjust credentials as needed)
export DATABASE_URL="postgresql://user:password@localhost:5432/image_tagger_v3"

# Run the FastAPI server
uvicorn student_app.main:app --reload --port 8000
```

### 3. Install frontend dependencies

```bash
cd TRS_v1.1/frontend
npm install
```

### 4. Run a single app

```bash
npm run dev:explorer    # Image browser at http://localhost:3004/explorer/
npm run dev:workbench   # Tagger UI at http://localhost:3001/workbench/
npm run dev:admin       # Admin panel at http://localhost:3003/admin/
npm run dev:monitor     # System monitor at http://localhost:3002/monitor/
```

### 5. Run all apps at once

```bash
npm run dev:all
```

## App Descriptions

### Explorer (port 3004)
Browse and search images with attribute filters. Features:
- Text search + attribute sidebar filtering
- Debug overlays: edges, depth, segmentation, complexity, room type, materials
- Masonry grid with tag badges and affordance scores
- Cart system for dataset export (JSON)
- Image detail modal with full science attributes and human validations

### Workbench (port 3001)
Human-in-the-loop annotation interface for taggers.

### Admin (port 3003)
- Image upload management
- VLM engine configuration
- Science pipeline run management
- Cost/budget dashboard

### Monitor (port 3002)
- System health monitoring
- Tagger velocity tracking
- Inter-rater reliability metrics

## Backend API Dependency

The frontend depends on the student branch backend (`student_app/`), which
provides these API groups:

| Route prefix | File | Frontend consumer |
|---|---|---|
| `/v1/explorer/` | `v1_discovery.py` | Explorer |
| `/v1/annotation/` | `v1_annotation.py` | Workbench |
| `/v1/admin/` | `v1_admin.py` | Admin |
| `/v1/supervision/` | `v1_supervision.py` | Monitor |
| `/v1/debug/` | `v1_debug.py` | Explorer debug overlays |
| `/v1/features/` | `v1_features.py` | Explorer attribute sidebar |
| `/v1/vlm-health/` | `v1_vlm_health.py` | Monitor |
| `/v1/bn-export/` | `v1_bn_export.py` | Admin |

## Import Path Note

The student backend code uses `from backend.xxx` import paths. When running
from `TRS_v1.1/`, you have two options:

1. **Symlink approach** (recommended for dev):
   ```bash
   cd TRS_v1.1
   ln -s backend/student_app backend_link
   # Then run: PYTHONPATH=. uvicorn backend_link.main:app
   ```

2. **Direct path**: Set `PYTHONPATH` to include the student_app parent:
   ```bash
   cd TRS_v1.1/backend
   PYTHONPATH=student_app uvicorn student_app.main:app
   ```

## Building for Production

```bash
cd frontend
npm run build
# Output goes to frontend/dist/{explorer,workbench,admin,monitor}/
```
