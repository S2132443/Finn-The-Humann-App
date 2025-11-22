"""Settings API endpoints for configuration management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from app.database import get_db
from app.models.currency import Currency
from app.models.asset import AssetClass
from app.models.allocation import StrategicAllocation
from app.schemas.currency import CurrencyResponse, CurrencyUpdate
from app.schemas.asset import AssetClassResponse, AssetClassCreate
from app.schemas.allocation import StrategicAllocationCreate, StrategicAllocationResponse

router = APIRouter()


# Currency endpoints
@router.get("/currencies", response_model=List[CurrencyResponse])
def get_currencies(db: Session = Depends(get_db)):
    """Get all currencies with exchange rates."""
    return db.query(Currency).all()


@router.put("/currencies/{currency_code}", response_model=CurrencyResponse)
def update_currency_rate(
    currency_code: str,
    currency_update: CurrencyUpdate,
    db: Session = Depends(get_db)
):
    """Update currency exchange rate."""
    currency = db.query(Currency).filter(Currency.code == currency_code).first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency {currency_code} not found"
        )
    
    currency.exchange_rate_to_myr = currency_update.exchange_rate_to_myr
    db.commit()
    db.refresh(currency)
    return currency


# Asset Class endpoints
@router.get("/asset-classes", response_model=List[AssetClassResponse])
def get_all_asset_classes(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all asset classes."""
    query = db.query(AssetClass)
    if not include_inactive:
        query = query.filter(AssetClass.is_active == True)
    return query.order_by(AssetClass.display_order).all()


@router.post("/asset-classes", response_model=AssetClassResponse, status_code=status.HTTP_201_CREATED)
def create_asset_class(
    asset_class: AssetClassCreate,
    db: Session = Depends(get_db)
):
    """Create a new asset class."""
    # Check for duplicate name
    existing = db.query(AssetClass).filter(AssetClass.name == asset_class.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset class '{asset_class.name}' already exists"
        )
    
    db_class = AssetClass(**asset_class.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@router.put("/asset-classes/{class_id}", response_model=AssetClassResponse)
def update_asset_class(
    class_id: UUID,
    asset_class: AssetClassCreate,
    db: Session = Depends(get_db)
):
    """Update an asset class."""
    db_class = db.query(AssetClass).filter(AssetClass.id == class_id).first()
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset class not found"
        )
    
    for field, value in asset_class.model_dump().items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class


@router.delete("/asset-classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset_class(class_id: UUID, db: Session = Depends(get_db)):
    """Deactivate an asset class (soft delete)."""
    db_class = db.query(AssetClass).filter(AssetClass.id == class_id).first()
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset class not found"
        )
    
    db_class.is_active = False
    db.commit()
    return None


# Strategic Allocation endpoints
@router.get("/strategic-allocation", response_model=List[StrategicAllocationResponse])
def get_strategic_allocations(
    effective_date: date = None,
    db: Session = Depends(get_db)
):
    """Get strategic allocations (current or for a specific date)."""
    if not effective_date:
        effective_date = date.today()
    
    # Get latest allocation for each asset class
    allocations = []
    asset_classes = db.query(AssetClass).filter(AssetClass.is_active == True).all()
    
    for asset_class in asset_classes:
        allocation = db.query(StrategicAllocation).filter(
            StrategicAllocation.asset_class_id == asset_class.id,
            StrategicAllocation.effective_date <= effective_date
        ).order_by(StrategicAllocation.effective_date.desc()).first()
        
        if allocation:
            response = StrategicAllocationResponse.model_validate(allocation)
            response.asset_class_name = asset_class.name
            allocations.append(response)
    
    return allocations


@router.post("/strategic-allocation", response_model=StrategicAllocationResponse, status_code=status.HTTP_201_CREATED)
def create_strategic_allocation(
    allocation: StrategicAllocationCreate,
    db: Session = Depends(get_db)
):
    """Create or update strategic allocation for an asset class."""
    # Check if asset class exists
    asset_class = db.query(AssetClass).filter(
        AssetClass.id == allocation.asset_class_id
    ).first()
    
    if not asset_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset class not found"
        )
    
    # Check if allocation already exists for this date
    existing = db.query(StrategicAllocation).filter(
        StrategicAllocation.asset_class_id == allocation.asset_class_id,
        StrategicAllocation.effective_date == allocation.effective_date
    ).first()
    
    if existing:
        # Update existing
        existing.target_percentage = allocation.target_percentage
        existing.notes = allocation.notes
        db.commit()
        db.refresh(existing)
        response = StrategicAllocationResponse.model_validate(existing)
        response.asset_class_name = asset_class.name
        return response
    
    # Create new
    db_allocation = StrategicAllocation(**allocation.model_dump())
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    
    response = StrategicAllocationResponse.model_validate(db_allocation)
    response.asset_class_name = asset_class.name
    return response


@router.post("/strategic-allocation/bulk", response_model=List[StrategicAllocationResponse])
def bulk_update_strategic_allocation(
    allocations: List[StrategicAllocationCreate],
    db: Session = Depends(get_db)
):
    """Bulk update strategic allocations."""
    # Validate total percentage
    total = sum(a.target_percentage for a in allocations)
    if abs(total - 100) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total allocation must be 100%, got {total}%"
        )
    
    results = []
    for allocation in allocations:
        # Check if asset class exists
        asset_class = db.query(AssetClass).filter(
            AssetClass.id == allocation.asset_class_id
        ).first()
        
        if not asset_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset class {allocation.asset_class_id} not found"
            )
        
        # Check if allocation already exists for this date
        existing = db.query(StrategicAllocation).filter(
            StrategicAllocation.asset_class_id == allocation.asset_class_id,
            StrategicAllocation.effective_date == allocation.effective_date
        ).first()
        
        if existing:
            existing.target_percentage = allocation.target_percentage
            existing.notes = allocation.notes
            db.flush()
            response = StrategicAllocationResponse.model_validate(existing)
        else:
            db_allocation = StrategicAllocation(**allocation.model_dump())
            db.add(db_allocation)
            db.flush()
            response = StrategicAllocationResponse.model_validate(db_allocation)
        
        response.asset_class_name = asset_class.name
        results.append(response)
    
    db.commit()
    return results
