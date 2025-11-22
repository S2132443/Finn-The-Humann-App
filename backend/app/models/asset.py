"""Asset and AssetClass models."""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime, Date, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AssetClass(Base):
    """Asset class lookup table."""
    
    __tablename__ = "asset_classes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7), default="#6c757d")
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assets = relationship("Asset", back_populates="asset_class")
    strategic_allocations = relationship("StrategicAllocation", back_populates="asset_class")


class Asset(Base):
    """Individual asset/holding model."""
    
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    asset_class_id = Column(UUID(as_uuid=True), ForeignKey("asset_classes.id"))
    name = Column(String(255), nullable=False)
    symbol = Column(String(50))
    quantity = Column(Numeric(20, 8), default=0)
    current_price = Column(Numeric(20, 8))
    current_value = Column(Numeric(20, 2))
    currency = Column(String(3), ForeignKey("currencies.code"), default="MYR")
    cost_basis = Column(Numeric(20, 2))
    purchase_date = Column(Date)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="assets")
    asset_class = relationship("AssetClass", back_populates="assets")
    income_records = relationship("Income", back_populates="asset")
    currency_rel = relationship("Currency", foreign_keys=[currency])
