"""Account API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.account import Account, AccountType
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTypeResponse,
    AccountWithAssets,
)

router = APIRouter()


@router.get("/types", response_model=List[AccountTypeResponse])
def get_account_types(db: Session = Depends(get_db)):
    """Get all account types."""
    return db.query(AccountType).all()


@router.get("", response_model=List[AccountResponse])
def get_accounts(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    """Get all accounts."""
    query = db.query(Account)
    if not include_inactive:
        query = query.filter(Account.is_active == True)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account."""
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/{account_id}", response_model=AccountWithAssets)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    """Get account by ID with assets."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    # Calculate total value
    total_value = sum(
        float(asset.current_value or 0) for asset in account.assets if asset.is_active
    )

    # Create response with total value
    response = AccountWithAssets.model_validate(account)
    response.total_value = total_value
    return response


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: UUID, account_update: AccountUpdate, db: Session = Depends(get_db)
):
    """Update an account."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    update_data = account_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: UUID, db: Session = Depends(get_db)):
    """Delete an account (soft delete)."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    # Soft delete
    account.is_active = False
    db.commit()
    return None
