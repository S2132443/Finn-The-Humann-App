"""Market page web routes."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.asset import Asset, AssetClass
from app.models.market_price import MarketPrice
from app.web.dependencies import templates, flash

router = APIRouter()


def _get_market_data(db: Session):
    """Get all market prices with owned quantity info."""
    tracked = db.query(MarketPrice).order_by(MarketPrice.symbol).all()
    asset_classes = {ac.id: ac for ac in db.query(AssetClass).all()}

    # Sum owned quantities per symbol
    owned = {}
    assets = (
        db.query(Asset)
        .filter(
            Asset.is_active == True,
            Asset.symbol != None,
            Asset.symbol != "",
        )
        .all()
    )
    for a in assets:
        if a.symbol in owned:
            owned[a.symbol]["quantity"] += float(a.quantity or 0)
            owned[a.symbol]["value"] += float(a.current_value or 0)
        else:
            owned[a.symbol] = {
                "quantity": float(a.quantity or 0),
                "value": float(a.current_value or 0),
            }

    result = []
    for mp in tracked:
        ac = asset_classes.get(mp.asset_class_id)
        current = float(mp.current_price) if mp.current_price else 0
        previous = float(mp.previous_price) if mp.previous_price else 0
        change = current - previous if previous > 0 else 0
        change_pct = (change / previous * 100) if previous > 0 else 0
        own = owned.get(mp.symbol)

        result.append(
            {
                "symbol": mp.symbol,
                "name": mp.name,
                "current_price": current,
                "previous_price": previous,
                "price_myr": float(mp.price_myr) if mp.price_myr else current,
                "currency": mp.currency or "MYR",
                "change": change,
                "change_pct": change_pct,
                "source": mp.source,
                "updated_at": mp.updated_at,
                "asset_class_name": ac.name if ac else None,
                "color": ac.color if ac else None,
                "owned_qty": own["quantity"] if own else None,
                "owned_value": own["value"] if own else None,
            }
        )
    return result


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """Market overview page."""
    market_data = _get_market_data(db)
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )
    return templates.TemplateResponse(
        "market/index.html",
        {
            "request": request,
            "market_data": market_data,
            "asset_classes": asset_classes,
        },
    )


@router.post("/add")
def add_symbol(
    request: Request,
    db: Session = Depends(get_db),
    symbol: str = Form(...),
    name: str = Form(...),
    asset_class_id: Optional[str] = Form(None),
    source: str = Form("yahoo"),
):
    """Add a symbol to the watchlist."""
    symbol = symbol.strip().upper()
    existing = db.query(MarketPrice).filter(MarketPrice.symbol == symbol).first()
    if existing:
        flash(request, f"{symbol} is already being tracked", "warning")
        return RedirectResponse(url="/market", status_code=303)

    mp = MarketPrice(
        symbol=symbol,
        name=name.strip(),
        asset_class_id=asset_class_id or None,
        source=source,
    )
    db.add(mp)
    db.commit()
    flash(request, f"Added {symbol} to watchlist", "success")
    return RedirectResponse(url="/market", status_code=303)


@router.post("/{symbol}/delete")
def delete_symbol(request: Request, symbol: str, db: Session = Depends(get_db)):
    """Remove a symbol from the watchlist."""
    mp = db.query(MarketPrice).filter(MarketPrice.symbol == symbol).first()
    if mp:
        db.delete(mp)
        db.commit()
        flash(request, f"Removed {symbol} from watchlist", "success")
    else:
        flash(request, f"{symbol} not found", "danger")
    return RedirectResponse(url="/market", status_code=303)
