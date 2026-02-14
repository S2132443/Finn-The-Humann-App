"""Price refresh API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.price_fetcher import update_all_prices, update_exchange_rates

router = APIRouter()


@router.post("/refresh")
async def refresh_prices(db: Session = Depends(get_db)):
    """Trigger on-demand price update for all tracked symbols.

    Updates exchange rates first, then fetches prices from LUNO and Yahoo Finance.
    Pushes updated prices to matching portfolio assets.
    """
    rate_result = await update_exchange_rates(db)
    price_result = await update_all_prices(db)
    return {
        "prices": price_result,
        "exchange_rates": rate_result,
    }
