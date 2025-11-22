"""Strategic Asset Allocation model."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class StrategicAllocation(Base):
    """Strategic asset allocation targets."""
    
    __tablename__ = "strategic_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_class_id = Column(UUID(as_uuid=True), ForeignKey("asset_classes.id", ondelete="CASCADE"))
    target_percentage = Column(Numeric(5, 2), nullable=False)
    effective_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    asset_class = relationship("AssetClass", back_populates="strategic_allocations")
