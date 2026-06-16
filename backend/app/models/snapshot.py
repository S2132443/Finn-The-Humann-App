"""Monthly and Asset snapshot models for historical tracking."""

from sqlalchemy import Column, String, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class MonthlySnapshot(Base):
    """Monthly portfolio snapshot for historical tracking."""

    __tablename__ = "monthly_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date = Column(Date, nullable=False, unique=True)
    total_assets = Column(Numeric(20, 2), nullable=False)
    total_liabilities = Column(Numeric(20, 2), nullable=False)
    net_worth = Column(Numeric(20, 2), nullable=False)
    allocation_data = Column(JSONB)  # Store allocation breakdown as JSON
    performance_data = Column(JSONB)  # Store performance metrics as JSON
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    asset_snapshots = relationship(
        "AssetSnapshot", back_populates="monthly_snapshot", cascade="all, delete-orphan"
    )


class AssetSnapshot(Base):
    """Individual asset snapshot within a monthly snapshot."""

    __tablename__ = "asset_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monthly_snapshot_id = Column(
        UUID(as_uuid=True), ForeignKey("monthly_snapshots.id", ondelete="CASCADE")
    )
    asset_id = Column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )
    asset_name = Column(String(255), nullable=False)
    asset_class_id = Column(UUID(as_uuid=True), ForeignKey("asset_classes.id"))
    value = Column(Numeric(20, 2), nullable=False)
    quantity = Column(Numeric(20, 8))
    currency = Column(String(3), ForeignKey("currencies.code"), default="MYR")
    value_in_myr = Column(Numeric(20, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    monthly_snapshot = relationship("MonthlySnapshot", back_populates="asset_snapshots")
