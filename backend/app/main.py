"""Main FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings

from app.api.v1 import (
    accounts,
    assets,
    transactions,
    income,
    calculations,
    snapshots,
    settings as settings_router,
    prices,
    brokers,
    market,
)
import app.services.brokers.luno  # noqa: F401 — triggers provider registration

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Investment Portfolio Tracking Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(income.router, prefix="/api/v1/income", tags=["Income"])
app.include_router(calculations.router, prefix="/api/v1", tags=["Calculations"])
app.include_router(snapshots.router, prefix="/api/v1/snapshots", tags=["Snapshots"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])
app.include_router(brokers.router, prefix="/api/v1/brokers", tags=["Brokers"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1", tags=["API Info"])
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "base_currency": settings.BASE_CURRENCY,
        "endpoints": {
            "accounts": "/api/v1/accounts",
            "assets": "/api/v1/assets",
            "transactions": "/api/v1/transactions",
            "income": "/api/v1/income",
            "networth": "/api/v1/networth",
            "allocation": "/api/v1/allocation",
            "returns": "/api/v1/returns",
            "snapshots": "/api/v1/snapshots",
            "settings": "/api/v1/settings",
            "prices": "/api/v1/prices",
            "brokers": "/api/v1/brokers",
        },
    }


# --- SPA (React + Vite build) ---------------------------------------------
# FRONTEND_DIST lives at repo-root/frontend/dist. The Dockerfile copies it
# there; locally, `cd frontend && npm run build` produces it.
FRONTEND_DIST = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)

if os.path.isdir(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="spa_assets")

    @app.get("/{filename:path}", include_in_schema=False)
    async def spa_fallback(filename: str):
        # Let unknown /api, /docs, /redoc, /health paths 404 as JSON — don't
        # mask them with index.html (which would break fetch().json()).
        if filename.startswith(("api/", "docs", "redoc", "health", "openapi.json")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = os.path.join(FRONTEND_DIST, filename)
        if filename and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
