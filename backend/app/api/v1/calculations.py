"""Calculation API endpoints for net worth, allocation, and returns."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from app.database import get_db
from app.models.account import Account
from app.models.asset import Asset, AssetClass
from app.models.transaction import Transaction
from app.models.income import Income
from app.models.snapshot import MonthlySnapshot
from app.models.currency import Currency
from app.models.allocation import StrategicAllocation
from app.schemas.calculations import (
    NetWorthResponse, NetWorthHistory, NetWorthHistoryItem,
    TWRRResponse, YieldResponse
)
from app.schemas.allocation import AllocationResponse, AllocationComparison
from app.config import settings

router = APIRouter()


def get_exchange_rate(db: Session, currency_code: str) -> float:
    """Get exchange rate to MYR for a currency."""
    if currency_code == 'MYR':
        return 1.0
    currency = db.query(Currency).filter(Currency.code == currency_code).first()
    return float(currency.exchange_rate_to_myr) if currency else 1.0


@router.get("/networth", response_model=NetWorthResponse)
def get_current_networth(db: Session = Depends(get_db)):
    """Get current net worth calculation."""
    total_assets = 0.0
    total_liabilities = 0.0
    
    # Get all active accounts
    accounts = db.query(Account).filter(Account.is_active == True).all()
    
    for account in accounts:
        # Sum up assets in this account
        for asset in account.assets:
            if asset.is_active and asset.current_value:
                value_myr = float(asset.current_value) * get_exchange_rate(db, asset.currency)
                if account.is_liability:
                    total_liabilities += value_myr
                else:
                    total_assets += value_myr
    
    return NetWorthResponse(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        base_currency=settings.BASE_CURRENCY,
        as_of_date=date.today()
    )


@router.get("/networth/history", response_model=NetWorthHistory)
def get_networth_history(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get net worth history from monthly snapshots."""
    # Get snapshots for the requested period
    start_date = date.today() - relativedelta(months=months)
    
    snapshots = db.query(MonthlySnapshot).filter(
        MonthlySnapshot.snapshot_date >= start_date
    ).order_by(MonthlySnapshot.snapshot_date).all()
    
    history = []
    for snapshot in snapshots:
        history.append(NetWorthHistoryItem(
            date=snapshot.snapshot_date,
            total_assets=float(snapshot.total_assets),
            total_liabilities=float(snapshot.total_liabilities),
            net_worth=float(snapshot.net_worth)
        ))
    
    return NetWorthHistory(
        history=history,
        base_currency=settings.BASE_CURRENCY
    )


@router.get("/allocation", response_model=AllocationComparison)
def get_allocation_comparison(db: Session = Depends(get_db)):
    """Get current asset allocation vs strategic allocation."""
    # Get all active asset classes
    asset_classes = db.query(AssetClass).filter(
        AssetClass.is_active == True
    ).order_by(AssetClass.display_order).all()
    
    # Calculate total value per asset class
    allocations = []
    total_portfolio_value = 0.0
    class_values = {}
    
    for asset_class in asset_classes:
        class_value = 0.0
        
        # Get all assets in this class
        assets = db.query(Asset).filter(
            Asset.asset_class_id == asset_class.id,
            Asset.is_active == True
        ).all()
        
        for asset in assets:
            if asset.current_value:
                # Check if account is not a liability
                account = db.query(Account).filter(
                    Account.id == asset.account_id,
                    Account.is_active == True,
                    Account.is_liability == False
                ).first()
                
                if account:
                    value_myr = float(asset.current_value) * get_exchange_rate(db, asset.currency)
                    class_value += value_myr
        
        class_values[asset_class.id] = class_value
        total_portfolio_value += class_value
    
    # Build allocation response with percentages
    for asset_class in asset_classes:
        class_value = class_values[asset_class.id]
        percentage = (class_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        
        # Get strategic allocation target
        strategic = db.query(StrategicAllocation).filter(
            StrategicAllocation.asset_class_id == asset_class.id,
            StrategicAllocation.effective_date <= date.today()
        ).order_by(StrategicAllocation.effective_date.desc()).first()
        
        target_percentage = float(strategic.target_percentage) if strategic else 0.0
        
        allocations.append(AllocationResponse(
            asset_class_id=asset_class.id,
            asset_class_name=asset_class.name,
            color=asset_class.color,
            total_value=class_value,
            percentage=percentage,
            target_percentage=target_percentage
        ))
    
    return AllocationComparison(
        allocations=allocations,
        total_value=total_portfolio_value
    )


@router.get("/returns/twrr", response_model=TWRRResponse)
def calculate_twrr(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Calculate Time-Weighted Rate of Return (TWRR).
    
    TWRR measures the compound rate of growth, eliminating the distorting 
    effects of cash flows (deposits/withdrawals).
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - relativedelta(years=1)
    
    # Get snapshots for the period
    snapshots = db.query(MonthlySnapshot).filter(
        MonthlySnapshot.snapshot_date >= start_date,
        MonthlySnapshot.snapshot_date <= end_date
    ).order_by(MonthlySnapshot.snapshot_date).all()
    
    if len(snapshots) < 2:
        # Not enough data, return 0
        return TWRRResponse(
            twrr=0.0,
            annualized_twrr=0.0,
            period_start=start_date,
            period_end=end_date
        )
    
    # Get all transactions in the period
    transactions = db.query(Transaction).filter(
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).order_by(Transaction.transaction_date).all()
    
    # Build cash flow timeline
    cash_flows = {}
    for txn in transactions:
        txn_date = txn.transaction_date
        if txn_date not in cash_flows:
            cash_flows[txn_date] = 0.0
        
        amount = float(txn.amount) * get_exchange_rate(db, txn.currency)
        
        if txn.transaction_type in ['deposit', 'transfer_in']:
            cash_flows[txn_date] += amount
        elif txn.transaction_type in ['withdrawal', 'transfer_out']:
            cash_flows[txn_date] -= amount
    
    # Calculate sub-period returns
    sub_period_returns = []
    cumulative_return = 1.0
    
    for i in range(1, len(snapshots)):
        prev_snapshot = snapshots[i - 1]
        curr_snapshot = snapshots[i]
        
        beginning_value = float(prev_snapshot.net_worth)
        ending_value = float(curr_snapshot.net_worth)
        
        # Sum cash flows between snapshots
        period_cash_flow = 0.0
        for cf_date, cf_amount in cash_flows.items():
            if prev_snapshot.snapshot_date < cf_date <= curr_snapshot.snapshot_date:
                period_cash_flow += cf_amount
        
        # Calculate sub-period return
        # HPR = (Ending Value - Cash Flow) / Beginning Value - 1
        if beginning_value > 0:
            hpr = (ending_value - period_cash_flow) / beginning_value - 1
        else:
            hpr = 0.0
        
        sub_period_returns.append({
            "period_start": prev_snapshot.snapshot_date.isoformat(),
            "period_end": curr_snapshot.snapshot_date.isoformat(),
            "return": hpr * 100  # Convert to percentage
        })
        
        cumulative_return *= (1 + hpr)
    
    # Calculate TWRR
    twrr = (cumulative_return - 1) * 100  # Convert to percentage
    
    # Calculate annualized TWRR
    days = (end_date - start_date).days
    years = days / 365.25
    if years > 0 and cumulative_return > 0:
        annualized_twrr = (pow(cumulative_return, 1/years) - 1) * 100
    else:
        annualized_twrr = 0.0
    
    return TWRRResponse(
        twrr=twrr,
        annualized_twrr=annualized_twrr,
        period_start=start_date,
        period_end=end_date,
        sub_period_returns=sub_period_returns
    )


@router.get("/yield", response_model=YieldResponse)
def calculate_yield(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Calculate investment yield (income / average portfolio value)."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - relativedelta(years=1)
    
    # Get total income for the period
    income_records = db.query(Income).filter(
        Income.income_date >= start_date,
        Income.income_date <= end_date
    ).all()
    
    total_income = 0.0
    for record in income_records:
        amount_myr = float(record.amount) * get_exchange_rate(db, record.currency)
        total_income += amount_myr
    
    # Get average portfolio value from snapshots
    snapshots = db.query(MonthlySnapshot).filter(
        MonthlySnapshot.snapshot_date >= start_date,
        MonthlySnapshot.snapshot_date <= end_date
    ).all()
    
    if snapshots:
        avg_value = sum(float(s.net_worth) for s in snapshots) / len(snapshots)
    else:
        # Use current net worth if no snapshots
        networth = get_current_networth(db)
        avg_value = networth.net_worth
    
    # Calculate yield
    yield_percentage = (total_income / avg_value * 100) if avg_value > 0 else 0.0
    
    # Annualize if period is not exactly one year
    days = (end_date - start_date).days
    if days > 0:
        annualized_yield = yield_percentage * (365 / days)
    else:
        annualized_yield = 0.0
    
    return YieldResponse(
        total_income=total_income,
        average_portfolio_value=avg_value,
        yield_percentage=yield_percentage,
        period_start=start_date,
        period_end=end_date,
        annualized_yield=annualized_yield
    )
