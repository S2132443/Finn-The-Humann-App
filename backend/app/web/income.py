"""Income web routes."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.income import Income
from app.models.account import Account
from app.models.asset import Asset
from app.web.dependencies import templates, flash

router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """List all income records."""
    income_records = db.query(Income).order_by(Income.income_date.desc()).all()
    return templates.TemplateResponse(
        "income/index.html",
        {
            "request": request,
            "income_records": income_records,
        },
    )


@router.get("/add")
def add_form(request: Request, db: Session = Depends(get_db)):
    """Show add income form."""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    assets = db.query(Asset).filter(Asset.is_active == True).all()
    return templates.TemplateResponse(
        "income/form.html",
        {
            "request": request,
            "income": None,
            "accounts": accounts,
            "assets": assets,
        },
    )


@router.post("/add")
def add_submit(
    request: Request,
    db: Session = Depends(get_db),
    account_id: str = Form(...),
    income_type: str = Form(...),
    amount: str = Form(...),
    currency: str = Form("MYR"),
    income_date: str = Form(...),
    asset_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_reinvested: Optional[str] = Form(None),
):
    """Create new income record."""
    income = Income(
        account_id=account_id,
        asset_id=asset_id or None,
        income_type=income_type,
        amount=float(amount),
        currency=currency,
        income_date=income_date,
        description=description or None,
        is_reinvested=is_reinvested == "on",
    )
    db.add(income)
    db.commit()
    flash(request, "Income recorded successfully", "success")
    return RedirectResponse(url="/income", status_code=303)


@router.post("/{income_id}/delete")
def delete(request: Request, income_id: UUID, db: Session = Depends(get_db)):
    """Delete income record."""
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        flash(request, "Income record not found", "danger")
    else:
        db.delete(income)
        db.commit()
        flash(request, "Income record deleted successfully", "success")

    return RedirectResponse(url="/income", status_code=303)
