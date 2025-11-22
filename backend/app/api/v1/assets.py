"""Asset API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.asset import Asset, AssetClass
from app.models.currency import Currency
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse,
    AssetClassResponse, AssetClassCreate
)

router = APIRouter()


@router.get("/classes", response_model=List[AssetClassResponse])
def get_asset_classes(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all asset classes."""
    query = db.query(AssetClass)
    if not include_inactive:
        query = query.filter(AssetClass.is_active == True)
    return query.order_by(AssetClass.display_order).all()


@router.post("/classes", response_model=AssetClassResponse, status_code=status.HTTP_201_CREATED)
def create_asset_class(asset_class: AssetClassCreate, db: Session = Depends(get_db)):
    """Create a new asset class."""
    db_class = AssetClass(**asset_class.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@router.get("", response_model=List[AssetResponse])
def get_assets(
    skip: int = 0,
    limit: int = 100,
    account_id: UUID = None,
    asset_class_id: UUID = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all assets with optional filtering."""
    query = db.query(Asset)
    
    if not include_inactive:
        query = query.filter(Asset.is_active == True)
    if account_id:
        query = query.filter(Asset.account_id == account_id)
    if asset_class_id:
        query = query.filter(Asset.asset_class_id == asset_class_id)
    
    assets = query.offset(skip).limit(limit).all()
    
    # Calculate value in MYR for each asset
    result = []
    for asset in assets:
        asset_dict = AssetResponse.model_validate(asset)
        if asset.currency != 'MYR' and asset.current_value:
            currency = db.query(Currency).filter(Currency.code == asset.currency).first()
            if currency:
                asset_dict.value_in_myr = float(asset.current_value) * float(currency.exchange_rate_to_myr)
        else:
            asset_dict.value_in_myr = float(asset.current_value) if asset.current_value else 0
        result.append(asset_dict)
    
    return result


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """Create a new asset."""
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Get asset by ID."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Calculate value in MYR
    response = AssetResponse.model_validate(asset)
    if asset.currency != 'MYR' and asset.current_value:
        currency = db.query(Currency).filter(Currency.code == asset.currency).first()
        if currency:
            response.value_in_myr = float(asset.current_value) * float(currency.exchange_rate_to_myr)
    else:
        response.value_in_myr = float(asset.current_value) if asset.current_value else 0
    
    return response


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: UUID,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    update_data = asset_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    """Delete an asset (soft delete)."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Soft delete
    asset.is_active = False
    db.commit()
    return None
