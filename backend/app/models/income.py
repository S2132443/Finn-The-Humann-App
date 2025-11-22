"""Income model for dividends, rental, interest, etc."""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Income(Base):
    """Investment income model (dividends, rental, interest, etc.)."""
    
    __tablename__ = "income"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    income_type = Column(String(50), nullable=False)  # dividend, rental, interest, distribution
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(3), ForeignKey("currencies.code"), default="MYR")
    income_date = Column(Date, nullable=False)
    description = Column(Text)
    is_reinvested = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="income_records")
    account = relationship("Account", back_populates="income_records")
    currency_rel = relationship("Currency", foreign_keys=[currency])
