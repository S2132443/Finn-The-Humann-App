"""Generic broker sync API endpoints.

Works for any registered broker provider. No provider-specific code here.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.brokers import get_all_providers, get_provider

router = APIRouter()


@router.get("/")
async def list_brokers():
    """List all registered broker providers with their configuration status."""
    return [
        {
            "name": p.name,
            "display_name": p.display_name,
            "configured": p.is_configured(),
        }
        for p in get_all_providers()
    ]


@router.post("/{provider_name}/sync")
async def sync_broker(provider_name: str, db: Session = Depends(get_db)):
    """Sync balances from a specific broker provider."""
    provider = get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Unknown broker: {provider_name}")

    if not provider.is_configured():
        raise HTTPException(
            status_code=400,
            detail=f"{provider.display_name} API keys not configured. "
            f"Set {', '.join(provider.config_keys)} in your .env file.",
        )

    result = provider.sync_balances(db)

    return {
        "provider": result.provider,
        "synced": result.synced,
        "created": result.created,
        "zeroed": result.zeroed,
        "errors": result.errors,
    }
