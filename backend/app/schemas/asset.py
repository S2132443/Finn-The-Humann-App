"""Asset schemas for API validation."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date


class AssetClassResponse(BaseModel):
    """Asset class response schema."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    color: str = "#6c757d"
    display_order: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True


class AssetClassCreate(BaseModel):
    """Asset class creation schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#6c757d", max_length=7)
    display_order: int = 0


class AssetBase(BaseModel):
    """Base asset schema."""
    
    account_id: UUID
    asset_class_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, max_length=50)
    quantity: float = 0
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    currency: str = Field(default="MYR", max_length=3)
    cost_basis: Optional[float] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None


class AssetCreate(AssetBase):
    """Asset creation schema."""
    pass


class AssetUpdate(BaseModel):
    """Asset update schema."""
    
    account_id: Optional[UUID] = None
    asset_class_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, max_length=50)
    quantity: Optional[float] = None
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    currency: Optional[str] = Field(None, max_length=3)
    cost_basis: Optional[float] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class AssetResponse(AssetBase):
    """Asset response schema."""
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    asset_class: Optional[AssetClassResponse] = None
    value_in_myr: Optional[float] = None
    
    class Config:
        from_attributes = True
