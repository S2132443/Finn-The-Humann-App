"""Calculation schemas for API responses."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from uuid import UUID


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


class AssetClassReturn(BaseModel):
    """Per-asset-class return data for Modified Dietz."""

    asset_class_id: UUID
    asset_class_name: str
    beginning_market_value: float
    ending_market_value: float
    net_cashflow: float
    income: float
    weighted_cashflow: float
    return_percentage: float


class ModifiedDietzResponse(BaseModel):
    """Modified Dietz return response schema."""

    return_percentage: float
    beginning_market_value: float
    ending_market_value: float
    net_cashflow: float
    income: float
    weighted_cashflow: float
    period_start: date
    period_end: date
    total_days: int
    per_class_returns: Optional[List[AssetClassReturn]] = None


class DailyReturnPoint(BaseModel):
    """Single point in a daily performance series."""

    date: date
    cumulative_return: float  # Percentage


class DailyPerformanceSeriesResponse(BaseModel):
    """Daily step-function cumulative return series."""

    series: List[DailyReturnPoint]
    period_start: date
    period_end: date
    asset_class_id: Optional[UUID] = None
    asset_class_name: Optional[str] = None
