"""Snapshot API endpoints for historical data management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from app.database import get_db
from app.models.snapshot import MonthlySnapshot, AssetSnapshot
from app.models.account import Account
from app.models.asset import Asset
from app.models.currency import Currency
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse, SnapshotSummary

router = APIRouter()


def get_exchange_rate(db: Session, currency_code: str) -> float:
    """Get exchange rate to MYR for a currency."""
    if currency_code == "MYR":
        return 1.0
    currency = db.query(Currency).filter(Currency.code == currency_code).first()
    return float(currency.exchange_rate_to_myr) if currency else 1.0


@router.get("", response_model=List[SnapshotSummary])
def get_snapshots(skip: int = 0, limit: int = 24, db: Session = Depends(get_db)):
    """Get all monthly snapshots."""
    return (
        db.query(MonthlySnapshot)
        .order_by(MonthlySnapshot.snapshot_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=SnapshotResponse, status_code=status.HTTP_201_CREATED)
def create_snapshot(snapshot: SnapshotCreate, db: Session = Depends(get_db)):
    """Create a new monthly snapshot of current portfolio state."""
    # Check if snapshot already exists for this date
    existing = (
        db.query(MonthlySnapshot)
        .filter(MonthlySnapshot.snapshot_date == snapshot.snapshot_date)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Snapshot already exists for {snapshot.snapshot_date}",
        )

    # Calculate current portfolio values
    total_assets = 0.0
    total_liabilities = 0.0
    allocation_data = {}

    # Get all active accounts and their assets
    accounts = db.query(Account).filter(Account.is_active == True).all()
    asset_snapshots_data = []

    for account in accounts:
        for asset in account.assets:
            if asset.is_active and asset.current_value:
                value = float(asset.current_value)
                exchange_rate = get_exchange_rate(db, asset.currency)
                value_myr = value * exchange_rate

                if account.is_liability:
                    total_liabilities += value_myr
                else:
                    total_assets += value_myr

                # Track allocation by asset class
                if asset.asset_class_id:
                    class_id = str(asset.asset_class_id)
                    if class_id not in allocation_data:
                        allocation_data[class_id] = 0.0
                    allocation_data[class_id] += value_myr

                # Create asset snapshot data
                asset_snapshots_data.append(
                    {
                        "asset_id": asset.id,
                        "asset_name": asset.name,
                        "asset_class_id": asset.asset_class_id,
                        "value": value,
                        "quantity": float(asset.quantity) if asset.quantity else None,
                        "currency": asset.currency,
                        "value_in_myr": value_myr,
                    }
                )

    # Create monthly snapshot
    db_snapshot = MonthlySnapshot(
        snapshot_date=snapshot.snapshot_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        allocation_data=allocation_data,
        performance_data={},
    )
    db.add(db_snapshot)
    db.flush()  # Get the snapshot ID

    # Create asset snapshots
    for asset_data in asset_snapshots_data:
        db_asset_snapshot = AssetSnapshot(
            monthly_snapshot_id=db_snapshot.id, **asset_data
        )
        db.add(db_asset_snapshot)

    db.commit()
    db.refresh(db_snapshot)

    return db_snapshot


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
def get_snapshot(snapshot_id: UUID, db: Session = Depends(get_db)):
    """Get snapshot by ID with asset details."""
    snapshot = (
        db.query(MonthlySnapshot).filter(MonthlySnapshot.id == snapshot_id).first()
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found"
        )

    return snapshot


@router.delete("/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snapshot(snapshot_id: UUID, db: Session = Depends(get_db)):
    """Delete a snapshot."""
    snapshot = (
        db.query(MonthlySnapshot).filter(MonthlySnapshot.id == snapshot_id).first()
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found"
        )

    db.delete(snapshot)
    db.commit()
    return None


@router.get("/date/{snapshot_date}", response_model=SnapshotResponse)
def get_snapshot_by_date(snapshot_date: date, db: Session = Depends(get_db)):
    """Get snapshot by date."""
    snapshot = (
        db.query(MonthlySnapshot)
        .filter(MonthlySnapshot.snapshot_date == snapshot_date)
        .first()
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No snapshot found for {snapshot_date}",
        )

    return snapshot
