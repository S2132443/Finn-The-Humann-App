"""Market / watchlist API — minimal CRUD over market_prices table."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market_price import MarketPrice

router = APIRouter()


class MarketItemOut(BaseModel):
    symbol: str
    name: str
    price: float | None = None
    change_24h: float | None = None
    change_percentage_24h: float | None = None
    currency: str = "MYR"
    last_updated: str | None = None

    class Config:
        from_attributes = True


class WatchlistAdd(BaseModel):
    symbol: str
    name: str | None = None
    source: str = "manual"


def _to_out(mp: MarketPrice) -> MarketItemOut:
    current = float(mp.current_price) if mp.current_price is not None else None
    previous = float(mp.previous_price) if mp.previous_price is not None else None
    change = (current - previous) if (current is not None and previous is not None) else None
    pct = (change / previous * 100) if (change is not None and previous) else None
    return MarketItemOut(
        symbol=mp.symbol,
        name=mp.name,
        price=current,
        change_24h=change,
        change_percentage_24h=pct,
        currency=mp.currency or "MYR",
        last_updated=mp.updated_at.isoformat() if mp.updated_at else None,
    )


@router.get("", response_model=list[MarketItemOut])
def list_market(db: Session = Depends(get_db)):
    return [_to_out(mp) for mp in db.query(MarketPrice).all()]


@router.post("", response_model=MarketItemOut, status_code=201)
def add_to_watchlist(payload: WatchlistAdd, db: Session = Depends(get_db)):
    existing = db.query(MarketPrice).filter(MarketPrice.symbol == payload.symbol).first()
    if existing:
        return _to_out(existing)
    mp = MarketPrice(
        symbol=payload.symbol,
        name=payload.name or payload.symbol,
        source=payload.source,
    )
    db.add(mp)
    db.commit()
    db.refresh(mp)
    return _to_out(mp)


@router.delete("/{symbol}", status_code=204)
def remove_from_watchlist(symbol: str, db: Session = Depends(get_db)):
    mp = db.query(MarketPrice).filter(MarketPrice.symbol == symbol).first()
    if not mp:
        raise HTTPException(status_code=404, detail="Symbol not in watchlist")
    db.delete(mp)
    db.commit()
