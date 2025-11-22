"""Account and AccountType models."""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AccountType(Base):
    """Account type lookup table."""
    
    __tablename__ = "account_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="account_type")


class Account(Base):
    """Investment account model."""
    
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    account_type_id = Column(UUID(as_uuid=True), ForeignKey("account_types.id"))
    institution = Column(String(255))
    account_number = Column(String(100))
    currency = Column(String(3), ForeignKey("currencies.code"), default="MYR")
    is_liability = Column(Boolean, default=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account_type = relationship("AccountType", back_populates="accounts")
    assets = relationship("Asset", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    income_records = relationship("Income", back_populates="account", cascade="all, delete-orphan")
    currency_rel = relationship("Currency", foreign_keys=[currency])
