"""Income API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from typing import List
from uuid import UUID
from datetime import date

from app.database import get_db
from app.models.income import Income
from app.models.asset import Asset
from app.models.currency import Currency
from app.schemas.income import IncomeCreate, IncomeResponse, IncomeSummary

router = APIRouter()


@router.get("", response_model=List[IncomeResponse])
def get_income(
    skip: int = 0,
    limit: int = 100,
    account_id: UUID = None,
    asset_id: UUID = None,
    income_type: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get all income records with optional filtering."""
    query = db.query(Income)
    
    if account_id:
        query = query.filter(Income.account_id == account_id)
    if asset_id:
        query = query.filter(Income.asset_id == asset_id)
    if income_type:
        query = query.filter(Income.income_type == income_type)
    if start_date:
        query = query.filter(Income.income_date >= start_date)
    if end_date:
        query = query.filter(Income.income_date <= end_date)
    
    income_records = query.order_by(Income.income_date.desc()).offset(skip).limit(limit).all()
    
    # Add asset name to response
    result = []
    for record in income_records:
        response = IncomeResponse.model_validate(record)
        if record.asset:
            response.asset_name = record.asset.name
        result.append(response)
    
    return result


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
def create_income(income: IncomeCreate, db: Session = Depends(get_db)):
    """Create a new income record."""
    db_income = Income(**income.model_dump())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@router.get("/summary", response_model=IncomeSummary)
def get_income_summary(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get income summary with totals by type, month, and asset class."""
    query = db.query(Income).options(
        joinedload(Income.asset).joinedload(Asset.asset_class)
    )

    if start_date:
        query = query.filter(Income.income_date >= start_date)
    if end_date:
        query = query.filter(Income.income_date <= end_date)

    income_records = query.all()

    # Calculate totals
    total_income = 0.0
    by_type = {}
    by_month = {}
    by_asset_class = {}

    for record in income_records:
        # Convert to MYR if needed
        amount_myr = float(record.amount)
        if record.currency != 'MYR':
            currency = db.query(Currency).filter(Currency.code == record.currency).first()
            if currency:
                amount_myr = float(record.amount) * float(currency.exchange_rate_to_myr)

        total_income += amount_myr

        # By type
        if record.income_type not in by_type:
            by_type[record.income_type] = 0.0
        by_type[record.income_type] += amount_myr

        # By month
        month_key = record.income_date.strftime("%Y-%m")
        if month_key not in by_month:
            by_month[month_key] = {"month": month_key, "total": 0.0}
        by_month[month_key]["total"] += amount_myr

        # By asset class (via asset -> asset_class relationship)
        class_name = "Unassigned"
        if record.asset and record.asset.asset_class:
            class_name = record.asset.asset_class.name
        if class_name not in by_asset_class:
            by_asset_class[class_name] = 0.0
        by_asset_class[class_name] += amount_myr

    return IncomeSummary(
        total_income=total_income,
        by_type=by_type,
        by_month=list(by_month.values()),
        by_asset_class=by_asset_class
    )


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income_record(income_id: UUID, db: Session = Depends(get_db)):
    """Get income record by ID."""
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found"
        )
    
    response = IncomeResponse.model_validate(income)
    if income.asset:
        response.asset_name = income.asset.name
    return response


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: UUID, db: Session = Depends(get_db)):
    """Delete an income record."""
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income record not found"
        )
    
    db.delete(income)
    db.commit()
    return None
