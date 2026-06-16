"""Asset web routes."""

import json

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.asset import Asset, AssetClass
from app.models.account import Account
from app.models.currency import Currency
from app.services.calculations import get_exchange_rate
from app.services.brokers import sync_market_price as _sync_market_price
from app.web.dependencies import templates, flash

router = APIRouter()


def _get_assets_with_display_data(db: Session):
    """Get all active assets with display fields (class name, color, MYR value)."""
    assets = db.query(Asset).filter(Asset.is_active == True).all()
    result = []
    for asset in assets:
        value_myr = float(asset.current_value or 0) * get_exchange_rate(
            db, asset.currency
        )
        result.append(
            {
                "id": asset.id,
                "name": asset.name,
                "symbol": asset.symbol,
                "quantity": asset.quantity,
                "current_price": asset.current_price,
                "current_value": asset.current_value,
                "currency": asset.currency,
                "cost_basis": asset.cost_basis,
                "value_in_myr": value_myr,
                "asset_class_name": (
                    asset.asset_class.name if asset.asset_class else None
                ),
                "asset_class_id": asset.asset_class_id,
                "color": asset.asset_class.color if asset.asset_class else None,
            }
        )
    return result


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """List all assets."""
    assets = _get_assets_with_display_data(db)
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )
    return templates.TemplateResponse(
        "assets/index.html",
        {
            "request": request,
            "assets": assets,
            "asset_classes": asset_classes,
        },
    )


@router.get("/add")
def add_form(request: Request, db: Session = Depends(get_db)):
    """Show add asset form."""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )
    currencies = db.query(Currency).all()
    return templates.TemplateResponse(
        "assets/form.html",
        {
            "request": request,
            "asset": None,
            "accounts": accounts,
            "asset_classes": asset_classes,
            "currencies": currencies,
        },
    )


@router.post("/add")
def add_submit(
    request: Request,
    db: Session = Depends(get_db),
    account_id: str = Form(...),
    name: str = Form(...),
    asset_class_id: Optional[str] = Form(None),
    symbol: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    current_price: Optional[str] = Form(None),
    current_value: Optional[str] = Form(None),
    currency: str = Form("MYR"),
    cost_basis: Optional[str] = Form(None),
    purchase_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Create new asset."""
    asset = Asset(
        account_id=account_id,
        asset_class_id=asset_class_id or None,
        name=name,
        symbol=symbol or None,
        quantity=float(quantity) if quantity else 0,
        current_price=float(current_price) if current_price else None,
        current_value=float(current_value) if current_value else None,
        currency=currency,
        cost_basis=float(cost_basis) if cost_basis else None,
        purchase_date=purchase_date or None,
        notes=notes or None,
    )
    db.add(asset)
    db.commit()
    _sync_market_price(db, asset)
    db.commit()
    flash(request, "Asset created successfully", "success")
    return RedirectResponse(url="/assets", status_code=303)


@router.get("/bulk-update")
def bulk_update_form(request: Request, db: Session = Depends(get_db)):
    """Show bulk price update form."""
    assets = _get_assets_with_display_data(db)
    # Serialize for Alpine.js (UUIDs → strings, Decimals → floats)
    assets_for_json = []
    for a in assets:
        assets_for_json.append(
            {
                "id": str(a["id"]),
                "name": a["name"],
                "symbol": a["symbol"],
                "quantity": float(a["quantity"]) if a["quantity"] else 0,
                "current_price": float(a["current_price"]) if a["current_price"] else 0,
                "current_value": float(a["current_value"]) if a["current_value"] else 0,
                "asset_class_name": a["asset_class_name"],
                "color": a["color"],
            }
        )
    return templates.TemplateResponse(
        "assets/bulk_update.html",
        {
            "request": request,
            "assets": assets,
            "assets_json": json.dumps(assets_for_json),
        },
    )


@router.post("/bulk-update")
async def bulk_update_submit(request: Request, db: Session = Depends(get_db)):
    """Process bulk price update."""
    form = await request.form()
    asset_count = int(form.get("asset_count", 0))

    updated = 0
    for i in range(asset_count):
        asset_id = form.get(f"asset_id_{i}")
        if not asset_id:
            continue
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            continue

        price = form.get(f"current_price_{i}")
        value = form.get(f"current_value_{i}")
        quantity = form.get(f"quantity_{i}")

        if price:
            asset.current_price = float(price)
        if value:
            asset.current_value = float(value)
        if quantity:
            asset.quantity = float(quantity)
        updated += 1

    db.commit()
    flash(request, f"Successfully updated {updated} assets", "success")
    return RedirectResponse(url="/assets", status_code=303)


@router.get("/{asset_id}/edit")
def edit_form(request: Request, asset_id: UUID, db: Session = Depends(get_db)):
    """Show edit asset form."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        flash(request, "Asset not found", "danger")
        return RedirectResponse(url="/assets", status_code=303)

    accounts = db.query(Account).filter(Account.is_active == True).all()
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )
    currencies = db.query(Currency).all()
    return templates.TemplateResponse(
        "assets/form.html",
        {
            "request": request,
            "asset": asset,
            "accounts": accounts,
            "asset_classes": asset_classes,
            "currencies": currencies,
        },
    )


@router.post("/{asset_id}/edit")
def edit_submit(
    request: Request,
    asset_id: UUID,
    db: Session = Depends(get_db),
    account_id: str = Form(...),
    name: str = Form(...),
    asset_class_id: Optional[str] = Form(None),
    symbol: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    current_price: Optional[str] = Form(None),
    current_value: Optional[str] = Form(None),
    currency: str = Form("MYR"),
    cost_basis: Optional[str] = Form(None),
    purchase_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Update asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        flash(request, "Asset not found", "danger")
        return RedirectResponse(url="/assets", status_code=303)

    asset.account_id = account_id
    asset.asset_class_id = asset_class_id or None
    asset.name = name
    asset.symbol = symbol or None
    asset.quantity = float(quantity) if quantity else 0
    asset.current_price = float(current_price) if current_price else None
    asset.current_value = float(current_value) if current_value else None
    asset.currency = currency
    asset.cost_basis = float(cost_basis) if cost_basis else None
    asset.purchase_date = purchase_date or None
    asset.notes = notes or None
    db.commit()
    _sync_market_price(db, asset)
    db.commit()

    flash(request, "Asset updated successfully", "success")
    return RedirectResponse(url="/assets", status_code=303)


@router.post("/{asset_id}/delete")
def delete(request: Request, asset_id: UUID, db: Session = Depends(get_db)):
    """Delete asset (soft delete)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        flash(request, "Asset not found", "danger")
    else:
        asset.is_active = False
        db.commit()
        flash(request, "Asset deleted successfully", "success")

    return RedirectResponse(url="/assets", status_code=303)
