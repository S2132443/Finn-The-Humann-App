# syntax=docker/dockerfile:1.6
# Build context expected to be the repo root so both `frontend/` and `backend/`
# are visible. See docker-compose.yml for the matching `context: .` setting.

# --- Stage 1: build the React SPA ---
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
# `npm install` (not `npm ci`) so package.json changes don't require a
# pre-regenerated lockfile — the image is the source of truth for the build.
RUN npm install --no-audit --no-fund
COPY frontend/ ./
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# --- Stage 2: Python backend serving API + built SPA ---
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Backend app at /app/backend (so imports resolve as `app.*` when run from there).
COPY backend/ /app/backend/

# SPA build output at /frontend/dist — matches the path resolved by main.py
# (../.. from /app/backend/app → /frontend/dist).
COPY --from=frontend-build /build/dist /app/frontend/dist

WORKDIR /app/backend
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
