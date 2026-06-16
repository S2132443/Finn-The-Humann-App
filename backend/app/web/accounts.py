"""Account web routes."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.account import Account, AccountType
from app.models.currency import Currency
from app.models.asset import Asset
from app.services.calculations import get_exchange_rate
from app.web.dependencies import templates, flash

router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """List all accounts."""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    account_types = db.query(AccountType).all()

    # Build response dicts with computed fields
    accounts_data = []
    for acc in accounts:
        total_value = 0.0
        for asset in acc.assets:
            if asset.is_active and asset.current_value:
                total_value += float(asset.current_value) * get_exchange_rate(
                    db, asset.currency
                )
        accounts_data.append(
            {
                "id": acc.id,
                "name": acc.name,
                "account_type": acc.account_type,
                "institution": acc.institution,
                "currency": acc.currency,
                "is_liability": acc.is_liability,
                "description": acc.description,
                "total_value": total_value,
            }
        )

    return templates.TemplateResponse(
        "accounts/index.html",
        {
            "request": request,
            "accounts": accounts_data,
            "account_types": account_types,
        },
    )


@router.get("/add")
def add_form(request: Request, db: Session = Depends(get_db)):
    """Show add account form."""
    account_types = db.query(AccountType).all()
    currencies = db.query(Currency).all()
    return templates.TemplateResponse(
        "accounts/form.html",
        {
            "request": request,
            "account": None,
            "account_types": account_types,
            "currencies": currencies,
        },
    )


@router.post("/add")
def add_submit(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    account_type_id: Optional[str] = Form(None),
    institution: Optional[str] = Form(None),
    currency: str = Form("MYR"),
    is_liability: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
):
    """Create new account."""
    account = Account(
        name=name,
        account_type_id=account_type_id or None,
        institution=institution or None,
        currency=currency,
        is_liability=is_liability == "on",
        description=description or None,
    )
    db.add(account)
    db.commit()
    flash(request, "Account created successfully", "success")
    return RedirectResponse(url="/accounts", status_code=303)


@router.get("/{account_id}")
def view(request: Request, account_id: UUID, db: Session = Depends(get_db)):
    """View account details."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        flash(request, "Account not found", "danger")
        return RedirectResponse(url="/accounts", status_code=303)

    # Get assets with MYR values
    assets_data = []
    total_value = 0.0
    for asset in account.assets:
        if asset.is_active:
            value_myr = float(asset.current_value or 0) * get_exchange_rate(
                db, asset.currency
            )
            total_value += value_myr
            assets_data.append(
                {
                    "id": asset.id,
                    "name": asset.name,
                    "symbol": asset.symbol,
                    "quantity": asset.quantity,
                    "current_value": asset.current_value,
                    "currency": asset.currency,
                    "value_in_myr": value_myr,
                    "asset_class": asset.asset_class,
                }
            )

    return templates.TemplateResponse(
        "accounts/view.html",
        {
            "request": request,
            "account": account,
            "assets": assets_data,
            "total_value": total_value,
        },
    )


@router.get("/{account_id}/edit")
def edit_form(request: Request, account_id: UUID, db: Session = Depends(get_db)):
    """Show edit account form."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        flash(request, "Account not found", "danger")
        return RedirectResponse(url="/accounts", status_code=303)

    account_types = db.query(AccountType).all()
    currencies = db.query(Currency).all()
    return templates.TemplateResponse(
        "accounts/form.html",
        {
            "request": request,
            "account": account,
            "account_types": account_types,
            "currencies": currencies,
        },
    )


@router.post("/{account_id}/edit")
def edit_submit(
    request: Request,
    account_id: UUID,
    db: Session = Depends(get_db),
    name: str = Form(...),
    account_type_id: Optional[str] = Form(None),
    institution: Optional[str] = Form(None),
    currency: str = Form("MYR"),
    is_liability: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
):
    """Update account."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        flash(request, "Account not found", "danger")
        return RedirectResponse(url="/accounts", status_code=303)

    account.name = name
    account.account_type_id = account_type_id or None
    account.institution = institution or None
    account.currency = currency
    account.is_liability = is_liability == "on"
    account.description = description or None
    db.commit()

    flash(request, "Account updated successfully", "success")
    return RedirectResponse(url=f"/accounts/{account_id}", status_code=303)


@router.post("/{account_id}/delete")
def delete(request: Request, account_id: UUID, db: Session = Depends(get_db)):
    """Delete account (soft delete)."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        flash(request, "Account not found", "danger")
    else:
        account.is_active = False
        db.commit()
        flash(request, "Account deleted successfully", "success")

    return RedirectResponse(url="/accounts", status_code=303)
