"""Allocation schemas for API validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date


class StrategicAllocationCreate(BaseModel):
    """Strategic allocation creation schema."""

    asset_class_id: UUID
    target_percentage: float = Field(..., ge=0, le=100)
    effective_date: date
    notes: Optional[str] = None


class StrategicAllocationResponse(BaseModel):
    """Strategic allocation response schema."""

    id: UUID
    asset_class_id: UUID
    asset_class_name: Optional[str] = None
    target_percentage: float
    effective_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AllocationResponse(BaseModel):
    """Current allocation response schema."""

    asset_class_id: UUID
    asset_class_name: str
    color: str
    total_value: float
    percentage: float
    target_percentage: float


class AllocationComparison(BaseModel):
    """Allocation comparison (Actual vs SAA) response schema."""

    allocations: List[AllocationResponse]
    total_value: float

    # Historical data for charts
    history: Optional[List[dict]] = None
