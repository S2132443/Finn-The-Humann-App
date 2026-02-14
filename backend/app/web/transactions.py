"""Transaction web routes."""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.asset import AssetClass
from app.services.calculations import get_exchange_rate
from app.web.dependencies import templates, flash

router = APIRouter()


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """List all transactions."""
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    txn_data = []
    for txn in transactions:
        txn_data.append({
            "id": txn.id,
            "account": txn.account,
            "transaction_type": txn.transaction_type,
            "amount": txn.amount,
            "currency": txn.currency,
            "transaction_date": txn.transaction_date,
            "description": txn.description,
            "asset_class": txn.asset_class if hasattr(txn, 'asset_class') else None,
        })

    return templates.TemplateResponse("transactions/index.html", {
        "request": request,
        "transactions": txn_data,
    })


@router.get("/add")
def add_form(request: Request, db: Session = Depends(get_db)):
    """Show add transaction form."""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    asset_classes = db.query(AssetClass).filter(AssetClass.is_active == True).order_by(AssetClass.display_order).all()
    return templates.TemplateResponse("transactions/form.html", {
        "request": request,
        "transaction": None,
        "accounts": accounts,
        "asset_classes": asset_classes,
    })


@router.post("/add")
def add_submit(
    request: Request,
    db: Session = Depends(get_db),
    account_id: str = Form(...),
    transaction_type: str = Form(...),
    amount: str = Form(...),
    currency: str = Form("MYR"),
    transaction_date: str = Form(...),
    description: Optional[str] = Form(None),
    asset_class_id: Optional[str] = Form(None),
):
    """Create new transaction."""
    txn = Transaction(
        account_id=account_id,
        transaction_type=transaction_type,
        amount=float(amount),
        currency=currency,
        transaction_date=transaction_date,
        description=description or None,
        asset_class_id=asset_class_id or None,
    )
    db.add(txn)
    db.commit()
    flash(request, "Transaction recorded successfully", "success")
    return RedirectResponse(url="/transactions", status_code=303)


@router.post("/{transaction_id}/delete")
def delete(request: Request, transaction_id: UUID, db: Session = Depends(get_db)):
    """Delete transaction."""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        flash(request, "Transaction not found", "danger")
    else:
        db.delete(txn)
        db.commit()
        flash(request, "Transaction deleted successfully", "success")

    return RedirectResponse(url="/transactions", status_code=303)
