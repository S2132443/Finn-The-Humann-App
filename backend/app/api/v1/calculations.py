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
from app.models.snapshot import AssetSnapshot
from app.schemas.calculations import (
    NetWorthResponse, NetWorthHistory, NetWorthHistoryItem,
    TWRRResponse, YieldResponse,
    AssetClassReturn, ModifiedDietzResponse,
    DailyReturnPoint, DailyPerformanceSeriesResponse
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


# =============================================
# Modified Dietz Helpers
# =============================================


def get_snapshot_market_value_by_class(
    db: Session,
    snapshot: MonthlySnapshot,
    asset_class_id=None,
) -> float:
    """Sum asset_snapshots.value_in_myr for a snapshot, optionally filtered by class."""
    query = db.query(func.coalesce(func.sum(AssetSnapshot.value_in_myr), 0)).filter(
        AssetSnapshot.monthly_snapshot_id == snapshot.id
    )
    if asset_class_id:
        query = query.filter(AssetSnapshot.asset_class_id == asset_class_id)
    return float(query.scalar())


def compute_weighted_cashflows(
    db: Session,
    start_date: date,
    end_date: date,
    total_days: int,
    asset_class_id=None,
) -> tuple[float, float]:
    """Compute net cashflow and time-weighted cashflow for the period.

    Returns (net_cashflow, weighted_cashflow).
    """
    query = db.query(Transaction).filter(
        Transaction.transaction_date > start_date,
        Transaction.transaction_date <= end_date,
    )
    if asset_class_id:
        query = query.filter(Transaction.asset_class_id == asset_class_id)

    net_cf = 0.0
    weighted_cf = 0.0

    for txn in query.all():
        amount_myr = float(txn.amount) * get_exchange_rate(db, txn.currency)

        if txn.transaction_type in ("deposit", "transfer_in"):
            signed_amount = amount_myr
        elif txn.transaction_type in ("withdrawal", "transfer_out"):
            signed_amount = -amount_myr
        else:
            signed_amount = -amount_myr  # fees are outflows

        net_cf += signed_amount

        days_remaining = (end_date - txn.transaction_date).days
        weight = days_remaining / total_days if total_days > 0 else 0
        weighted_cf += signed_amount * weight

    return net_cf, weighted_cf


def compute_period_income(
    db: Session,
    start_date: date,
    end_date: date,
    asset_class_id=None,
) -> float:
    """Total income (in MYR) for the period, optionally by asset class."""
    query = db.query(Income).filter(
        Income.income_date > start_date,
        Income.income_date <= end_date,
    )

    if asset_class_id:
        # Income -> Asset -> asset_class_id
        query = query.join(Income.asset).filter(
            Asset.asset_class_id == asset_class_id
        )

    total = 0.0
    for record in query.all():
        total += float(record.amount) * get_exchange_rate(db, record.currency)
    return total


def compute_modified_dietz(
    beginning_mv: float,
    ending_mv: float,
    net_cf: float,
    income: float,
    weighted_cf: float,
) -> float:
    """Apply the Modified Dietz formula and return percentage."""
    denominator = beginning_mv + weighted_cf
    if denominator <= 0:
        return 0.0
    return ((ending_mv - beginning_mv - net_cf - income) / denominator) * 100


def find_snapshot_on_or_before(db: Session, target_date: date) -> MonthlySnapshot | None:
    """Find the closest snapshot on or before the given date."""
    return (
        db.query(MonthlySnapshot)
        .filter(MonthlySnapshot.snapshot_date <= target_date)
        .order_by(MonthlySnapshot.snapshot_date.desc())
        .first()
    )


@router.get("/returns/modified-dietz", response_model=ModifiedDietzResponse)
def calculate_modified_dietz(
    start_date: date = None,
    end_date: date = None,
    asset_class_id: str = None,
    db: Session = Depends(get_db),
):
    """Calculate Modified Dietz return for the portfolio or a single asset class.

    Modified Dietz adjusts for the timing of cash flows, giving a more
    accurate return than simple gain/loss when deposits and withdrawals
    occur throughout the period.

    Formula:
        Return = (End MV - Beg MV - Net CF - Income)
                 / (Beg MV + Weighted CF)
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, 1, 1)

    # Resolve optional asset class filter
    from uuid import UUID as PyUUID

    ac_id = None
    if asset_class_id:
        try:
            ac_id = PyUUID(asset_class_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid asset_class_id format")

    begin_snapshot = find_snapshot_on_or_before(db, start_date)
    end_snapshot = find_snapshot_on_or_before(db, end_date)

    if not begin_snapshot or not end_snapshot or begin_snapshot.id == end_snapshot.id:
        return ModifiedDietzResponse(
            return_percentage=0.0,
            beginning_market_value=0.0,
            ending_market_value=0.0,
            net_cashflow=0.0,
            income=0.0,
            weighted_cashflow=0.0,
            period_start=start_date,
            period_end=end_date,
            total_days=0,
        )

    total_days = (end_snapshot.snapshot_date - begin_snapshot.snapshot_date).days
    if total_days <= 0:
        total_days = 1

    beg_mv = get_snapshot_market_value_by_class(db, begin_snapshot, ac_id)
    end_mv = get_snapshot_market_value_by_class(db, end_snapshot, ac_id)
    net_cf, weighted_cf = compute_weighted_cashflows(
        db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, total_days, ac_id
    )
    income = compute_period_income(
        db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, ac_id
    )

    return_pct = compute_modified_dietz(beg_mv, end_mv, net_cf, income, weighted_cf)

    # Per-class breakdown (only when not filtering by a single class)
    per_class = None
    if not ac_id:
        per_class = []
        asset_classes = (
            db.query(AssetClass)
            .filter(AssetClass.is_active == True)
            .order_by(AssetClass.display_order)
            .all()
        )
        for ac in asset_classes:
            c_beg = get_snapshot_market_value_by_class(db, begin_snapshot, ac.id)
            c_end = get_snapshot_market_value_by_class(db, end_snapshot, ac.id)
            c_cf, c_wcf = compute_weighted_cashflows(
                db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, total_days, ac.id
            )
            c_income = compute_period_income(
                db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, ac.id
            )
            c_ret = compute_modified_dietz(c_beg, c_end, c_cf, c_income, c_wcf)
            per_class.append(AssetClassReturn(
                asset_class_id=ac.id,
                asset_class_name=ac.name,
                beginning_market_value=c_beg,
                ending_market_value=c_end,
                net_cashflow=c_cf,
                income=c_income,
                weighted_cashflow=c_wcf,
                return_percentage=c_ret,
            ))

    return ModifiedDietzResponse(
        return_percentage=return_pct,
        beginning_market_value=beg_mv,
        ending_market_value=end_mv,
        net_cashflow=net_cf,
        income=income,
        weighted_cashflow=weighted_cf,
        period_start=start_date,
        period_end=end_date,
        total_days=total_days,
        per_class_returns=per_class,
    )


@router.get("/returns/daily-series", response_model=DailyPerformanceSeriesResponse)
def get_daily_performance_series(
    start_date: date = None,
    end_date: date = None,
    asset_class_id: str = None,
    db: Session = Depends(get_db),
):
    """Generate a daily step-function cumulative return series.

    At each snapshot date the cumulative Modified Dietz return is recalculated
    from the period start. Between snapshots the return is carried forward,
    producing a step-function suitable for line charts.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, 1, 1)

    from uuid import UUID as PyUUID
    from datetime import timedelta

    ac_id = None
    ac_name = None
    if asset_class_id:
        try:
            ac_id = PyUUID(asset_class_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid asset_class_id format")
        ac_obj = db.query(AssetClass).filter(AssetClass.id == ac_id).first()
        if ac_obj:
            ac_name = ac_obj.name

    baseline = find_snapshot_on_or_before(db, start_date)
    if not baseline:
        return DailyPerformanceSeriesResponse(
            series=[],
            period_start=start_date,
            period_end=end_date,
            asset_class_id=ac_id,
            asset_class_name=ac_name,
        )

    # Get all snapshots strictly after baseline up to end_date
    snapshots_in_range = (
        db.query(MonthlySnapshot)
        .filter(
            MonthlySnapshot.snapshot_date > baseline.snapshot_date,
            MonthlySnapshot.snapshot_date <= end_date,
        )
        .order_by(MonthlySnapshot.snapshot_date)
        .all()
    )

    beg_mv = get_snapshot_market_value_by_class(db, baseline, ac_id)

    # Compute cumulative Modified Dietz at each snapshot date
    snapshot_returns = {}
    for snap in snapshots_in_range:
        total_days = (snap.snapshot_date - baseline.snapshot_date).days
        if total_days <= 0:
            continue
        end_mv = get_snapshot_market_value_by_class(db, snap, ac_id)
        net_cf, weighted_cf = compute_weighted_cashflows(
            db, baseline.snapshot_date, snap.snapshot_date, total_days, ac_id
        )
        income = compute_period_income(
            db, baseline.snapshot_date, snap.snapshot_date, ac_id
        )
        ret = compute_modified_dietz(beg_mv, end_mv, net_cf, income, weighted_cf)
        snapshot_returns[snap.snapshot_date] = ret

    # Build daily series with step-function carry-forward
    series = []
    current_return = 0.0
    day = start_date
    while day <= end_date:
        if day in snapshot_returns:
            current_return = snapshot_returns[day]
        series.append(DailyReturnPoint(date=day, cumulative_return=round(current_return, 4)))
        day += timedelta(days=1)

    return DailyPerformanceSeriesResponse(
        series=series,
        period_start=start_date,
        period_end=end_date,
        asset_class_id=ac_id,
        asset_class_name=ac_name,
    )
