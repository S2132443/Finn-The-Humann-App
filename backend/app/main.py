"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import accounts, assets, transactions, income, calculations, snapshots, settings as settings_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Investment Portfolio Tracking Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    accounts.router,
    prefix="/api/v1/accounts",
    tags=["Accounts"]
)

app.include_router(
    assets.router,
    prefix="/api/v1/assets",
    tags=["Assets"]
)

app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["Transactions"]
)

app.include_router(
    income.router,
    prefix="/api/v1/income",
    tags=["Income"]
)

app.include_router(
    calculations.router,
    prefix="/api/v1",
    tags=["Calculations"]
)

app.include_router(
    snapshots.router,
    prefix="/api/v1/snapshots",
    tags=["Snapshots"]
)

app.include_router(
    settings_router.router,
    prefix="/api/v1/settings",
    tags=["Settings"]
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


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
            "settings": "/api/v1/settings"
        }
    }
