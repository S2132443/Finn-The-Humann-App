"""Settings web routes."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.asset import AssetClass
from app.models.currency import Currency
from app.models.allocation import StrategicAllocation
from app.models.snapshot import MonthlySnapshot, AssetSnapshot
from app.models.account import Account
from app.models.asset import Asset
from app.services.calculations import get_exchange_rate
from app.web.dependencies import templates, flash

router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """Settings overview."""
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )
    currencies = db.query(Currency).all()

    # Get current strategic allocations
    allocations = []
    for ac in asset_classes:
        sa = (
            db.query(StrategicAllocation)
            .filter(
                StrategicAllocation.asset_class_id == ac.id,
                StrategicAllocation.effective_date <= date.today(),
            )
            .order_by(StrategicAllocation.effective_date.desc())
            .first()
        )
        allocations.append(
            {
                "asset_class_id": ac.id,
                "asset_class_name": ac.name,
                "target_percentage": float(sa.target_percentage) if sa else 0.0,
            }
        )

    return templates.TemplateResponse(
        "settings/index.html",
        {
            "request": request,
            "asset_classes": asset_classes,
            "currencies": currencies,
            "allocations": allocations,
        },
    )


@router.get("/allocation")
def allocation_form(request: Request, db: Session = Depends(get_db)):
    """Show strategic allocation form."""
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )

    allocations = []
    for ac in asset_classes:
        sa = (
            db.query(StrategicAllocation)
            .filter(
                StrategicAllocation.asset_class_id == ac.id,
                StrategicAllocation.effective_date <= date.today(),
            )
            .order_by(StrategicAllocation.effective_date.desc())
            .first()
        )
        allocations.append(
            {
                "asset_class_id": str(ac.id),
                "asset_class_name": ac.name,
                "target_percentage": float(sa.target_percentage) if sa else 0.0,
            }
        )

    return templates.TemplateResponse(
        "settings/allocation.html",
        {
            "request": request,
            "asset_classes": asset_classes,
            "allocations": allocations,
        },
    )


@router.post("/allocation")
async def allocation_submit(request: Request, db: Session = Depends(get_db)):
    """Update strategic allocations."""
    form = await request.form()
    effective_date_str = form.get("effective_date")

    asset_classes = db.query(AssetClass).filter(AssetClass.is_active == True).all()
    for ac in asset_classes:
        percentage = form.get(f"allocation_{ac.id}")
        if percentage is not None:
            pct = float(percentage)
            sa = StrategicAllocation(
                asset_class_id=ac.id,
                target_percentage=pct,
                effective_date=effective_date_str,
            )
            # Upsert: delete existing for same class+date, then insert
            db.query(StrategicAllocation).filter(
                StrategicAllocation.asset_class_id == ac.id,
                StrategicAllocation.effective_date == effective_date_str,
            ).delete()
            db.add(sa)

    db.commit()
    flash(request, "Strategic allocation updated successfully", "success")
    return RedirectResponse(url="/settings", status_code=303)


@router.get("/snapshots")
def snapshots(request: Request, db: Session = Depends(get_db)):
    """View snapshots."""
    snapshot_list = (
        db.query(MonthlySnapshot).order_by(MonthlySnapshot.snapshot_date.desc()).all()
    )
    return templates.TemplateResponse(
        "settings/snapshots.html",
        {
            "request": request,
            "snapshots": snapshot_list,
        },
    )


@router.post("/snapshots/create")
def create_snapshot(
    request: Request,
    db: Session = Depends(get_db),
    snapshot_date: str = Form(...),
):
    """Create a new monthly snapshot."""
    # Calculate current totals
    total_assets = 0.0
    total_liabilities = 0.0

    accounts = db.query(Account).filter(Account.is_active == True).all()
    active_assets = []

    for account in accounts:
        for asset in account.assets:
            if asset.is_active and asset.current_value:
                value_myr = float(asset.current_value) * get_exchange_rate(
                    db, asset.currency
                )
                if account.is_liability:
                    total_liabilities += value_myr
                else:
                    total_assets += value_myr
                active_assets.append((asset, value_myr))

    snapshot = MonthlySnapshot(
        snapshot_date=snapshot_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
    )
    db.add(snapshot)
    db.flush()

    # Create asset snapshots
    for asset, value_myr in active_assets:
        asset_snap = AssetSnapshot(
            monthly_snapshot_id=snapshot.id,
            asset_id=asset.id,
            asset_name=asset.name,
            asset_class_id=asset.asset_class_id,
            value=float(asset.current_value),
            quantity=float(asset.quantity) if asset.quantity else None,
            currency=asset.currency,
            value_in_myr=value_myr,
        )
        db.add(asset_snap)

    db.commit()
    flash(request, "Snapshot created successfully", "success")
    return RedirectResponse(url="/settings/snapshots", status_code=303)
