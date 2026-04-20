# Finn - Personal Investment Tracker

Finn is a modern, professional personal investment tracker SPA built with React 18, TypeScript, Vite, and Tailwind CSS.

## Features

- **Dashboard**: KPI tiles, Net Worth history, and Asset Allocation charts.
- **Accounts**: Manage bank and brokerage accounts.
- **Assets**: Track portfolio performance with real-time price refreshes.
- **Market**: Watchlist with live market data.
- **Transactions**: Full history of investment activities.
- **Income**: Track passive income and dividends.
- **Mobile First**: Fully responsive design with bottom navigation and card-based mobile layouts.
- **Dark Mode**: Default dark theme with light mode toggle.

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS, shadcn/ui
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router 6
- **Charts**: Recharts
- **Animations**: Framer Motion

## Getting Started

### Prerequisites

- Node.js (v18 or later)
- npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

## Backend Integration (FastAPI)

Finn is designed to consume a FastAPI backend. The development server includes a proxy to bypass CORS issues.

### Mount in FastAPI

To serve the frontend from FastAPI in production:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API routes here
# app.include_router(api_router, prefix="/api/v1")

# Mount the frontend build directory
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

### Environment Variables

- `VITE_API_BASE_URL`: The base URL for the API (default: `http://localhost:8000/api/v1`).

## Build

To build the project for production:

```bash
npm run build
```

The output will be in the `dist/` directory.
