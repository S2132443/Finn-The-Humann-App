"""Market price model for price tracking and watchlist."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class MarketPrice(Base):
    """Tracked symbol with latest price data."""

    __tablename__ = "market_prices"

    symbol = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    asset_class_id = Column(UUID(as_uuid=True), ForeignKey("asset_classes.id"))
    current_price = Column(Numeric(20, 8))
    previous_price = Column(Numeric(20, 8))
    currency = Column(String(3), default="MYR")
    price_myr = Column(Numeric(20, 2))
    source = Column(String(20), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    asset_class = relationship("AssetClass")
