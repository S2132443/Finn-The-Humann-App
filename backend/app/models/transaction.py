"""Transaction model."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Transaction(Base):
    """Financial transaction model (deposits, withdrawals, etc.)."""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    transaction_type = Column(String(50), nullable=False)  # deposit, withdrawal, transfer, fee
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(3), ForeignKey("currencies.code"), default="MYR")
    transaction_date = Column(Date, nullable=False)
    description = Column(Text)
    reference = Column(String(255))
    asset_class_id = Column(UUID(as_uuid=True), ForeignKey("asset_classes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    asset_class = relationship("AssetClass")
    currency_rel = relationship("Currency", foreign_keys=[currency])
