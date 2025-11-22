"""Account schemas for API validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AccountTypeResponse(BaseModel):
    """Account type response schema."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    """Base account schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    account_type_id: Optional[UUID] = None
    institution: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="MYR", max_length=3)
    is_liability: bool = False
    description: Optional[str] = None


class AccountCreate(AccountBase):
    """Account creation schema."""
    pass


class AccountUpdate(BaseModel):
    """Account update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_type_id: Optional[UUID] = None
    institution: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=3)
    is_liability: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    """Account response schema."""
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    account_type: Optional[AccountTypeResponse] = None
    
    class Config:
        from_attributes = True


class AssetSummary(BaseModel):
    """Brief asset summary for account view."""
    
    id: UUID
    name: str
    current_value: Optional[float] = None
    currency: str
    
    class Config:
        from_attributes = True


class AccountWithAssets(AccountResponse):
    """Account with nested assets."""
    
    assets: List[AssetSummary] = []
    total_value: float = 0.0
