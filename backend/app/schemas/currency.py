"""Currency schemas for API validation."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CurrencyResponse(BaseModel):
    """Currency response schema."""
    
    code: str
    name: str
    symbol: Optional[str] = None
    exchange_rate_to_myr: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CurrencyUpdate(BaseModel):
    """Currency update schema (for exchange rates)."""
    
    exchange_rate_to_myr: float
