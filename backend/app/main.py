"""Main FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
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
)
import app.services.brokers.luno  # noqa: F401 — triggers provider registration
from app.web import dashboard as web_dashboard
from app.web import accounts as web_accounts
from app.web import assets as web_assets
from app.web import transactions as web_transactions
from app.web import income as web_income
from app.web import settings as web_settings
from app.web import market as web_market

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Investment Portfolio Tracking Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Session middleware (for flash messages and future auth)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])

app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])

app.include_router(
    transactions.router, prefix="/api/v1/transactions", tags=["Transactions"]
)

app.include_router(income.router, prefix="/api/v1/income", tags=["Income"])

app.include_router(calculations.router, prefix="/api/v1", tags=["Calculations"])

app.include_router(snapshots.router, prefix="/api/v1/snapshots", tags=["Snapshots"])

app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])

app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])

app.include_router(brokers.router, prefix="/api/v1/brokers", tags=["Brokers"])

# Web routes (HTML pages - served by FastAPI directly)
app.include_router(web_dashboard.router, tags=["Web"])
app.include_router(web_accounts.router, prefix="/accounts", tags=["Web"])
app.include_router(web_assets.router, prefix="/assets", tags=["Web"])
app.include_router(web_transactions.router, prefix="/transactions", tags=["Web"])
app.include_router(web_income.router, prefix="/income", tags=["Web"])
app.include_router(web_settings.router, prefix="/settings", tags=["Web"])
app.include_router(web_market.router, prefix="/market", tags=["Web"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1", tags=["API Info"])
async def api_info():
    """API information endpoint."""
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
