"""Transaction schemas for API validation."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date


class TransactionBase(BaseModel):
    """Base transaction schema."""
    
    account_id: UUID
    transaction_type: str = Field(..., min_length=1, max_length=50)  # deposit, withdrawal, transfer, fee
    amount: float
    currency: str = Field(default="MYR", max_length=3)
    transaction_date: date
    description: Optional[str] = None
    reference: Optional[str] = Field(None, max_length=255)


class TransactionCreate(TransactionBase):
    """Transaction creation schema."""
    pass


class TransactionResponse(TransactionBase):
    """Transaction response schema."""
    
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
