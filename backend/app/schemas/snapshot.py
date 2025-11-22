"""Snapshot schemas for API validation."""

from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, date


class SnapshotCreate(BaseModel):
    """Snapshot creation schema."""
    
    snapshot_date: date


class AssetSnapshotResponse(BaseModel):
    """Asset snapshot response schema."""
    
    id: UUID
    asset_name: str
    value: float
    quantity: Optional[float] = None
    currency: str
    value_in_myr: float
    
    class Config:
        from_attributes = True


class SnapshotResponse(BaseModel):
    """Monthly snapshot response schema."""
    
    id: UUID
    snapshot_date: date
    total_assets: float
    total_liabilities: float
    net_worth: float
    allocation_data: Optional[dict] = None
    performance_data: Optional[dict] = None
    created_at: datetime
    asset_snapshots: List[AssetSnapshotResponse] = []
    
    class Config:
        from_attributes = True


class SnapshotSummary(BaseModel):
    """Snapshot summary for listing."""
    
    id: UUID
    snapshot_date: date
    total_assets: float
    total_liabilities: float
    net_worth: float
    created_at: datetime
    
    class Config:
        from_attributes = True
