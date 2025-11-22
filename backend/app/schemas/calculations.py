"""Calculation schemas for API responses."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class NetWorthResponse(BaseModel):
    """Current net worth response schema."""
    
    total_assets: float
    total_liabilities: float
    net_worth: float
    base_currency: str = "MYR"
    as_of_date: date


class NetWorthHistoryItem(BaseModel):
    """Single net worth history item."""
    
    date: date
    total_assets: float
    total_liabilities: float
    net_worth: float


class NetWorthHistory(BaseModel):
    """Net worth history response schema."""
    
    history: List[NetWorthHistoryItem]
    base_currency: str = "MYR"


class TWRRResponse(BaseModel):
    """Time-Weighted Rate of Return response schema."""
    
    twrr: float  # As percentage
    annualized_twrr: Optional[float] = None
    period_start: date
    period_end: date
    sub_period_returns: Optional[List[dict]] = None


class YieldResponse(BaseModel):
    """Yield calculation response schema."""
    
    total_income: float
    average_portfolio_value: float
    yield_percentage: float
    period_start: date
    period_end: date
    annualized_yield: Optional[float] = None
