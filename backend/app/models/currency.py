"""Currency model for multi-currency support."""

from sqlalchemy import Column, String, DateTime, Numeric
from datetime import datetime

from app.database import Base


class Currency(Base):
    """Currency lookup table with exchange rates."""
    
    __tablename__ = "currencies"
    
    code = Column(String(3), primary_key=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10))
    exchange_rate_to_myr = Column(Numeric(15, 6), default=1.0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
