"""Income schemas for API validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


class IncomeBase(BaseModel):
    """Base income schema."""
    
    asset_id: Optional[UUID] = None
    account_id: UUID
    income_type: str = Field(..., min_length=1, max_length=50)  # dividend, rental, interest, distribution
    amount: float
    currency: str = Field(default="MYR", max_length=3)
    income_date: date
    description: Optional[str] = None
    is_reinvested: bool = False


class IncomeCreate(IncomeBase):
    """Income creation schema."""
    pass


class IncomeResponse(IncomeBase):
    """Income response schema."""
    
    id: UUID
    created_at: datetime
    asset_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class IncomeSummary(BaseModel):
    """Income summary for dashboard."""
    
    total_income: float
    by_type: dict[str, float]
    by_month: List[dict]
    yield_percentage: Optional[float] = None
