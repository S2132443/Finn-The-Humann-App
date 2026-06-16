"""Calculation API endpoints for net worth, allocation, and returns."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from dateutil.relativedelta import relativedelta

from app.database import get_db
from app.models.snapshot import MonthlySnapshot
from app.models.income import Income
from app.config import settings
from app.schemas.calculations import (
    NetWorthResponse,
    NetWorthHistory,
    NetWorthHistoryItem,
    TWRRResponse,
    YieldResponse,
    AssetClassReturn,
    ModifiedDietzResponse,
    DailyReturnPoint,
    DailyPerformanceSeriesResponse,
)
from app.schemas.allocation import AllocationResponse, AllocationComparison
from app.services.calculations import (
    get_exchange_rate,
    calculate_networth,
    get_networth_history as svc_networth_history,
    get_allocation_comparison as svc_allocation_comparison,
    get_snapshot_market_value_by_class,
    compute_weighted_cashflows,
    compute_period_income,
    compute_modified_dietz,
    find_snapshot_on_or_before,
)

router = APIRouter()


@router.get("/networth", response_model=NetWorthResponse)
def get_current_networth(db: Session = Depends(get_db)):
    """Get current net worth calculation."""
    data = calculate_networth(db)
    return NetWorthResponse(**data)


@router.get("/networth/history", response_model=NetWorthHistory)
def get_networth_history(months: int = 12, db: Session = Depends(get_db)):
    """Get net worth history from monthly snapshots."""
    history = svc_networth_history(db, months)
    return NetWorthHistory(
        history=[NetWorthHistoryItem(**item) for item in history],
        base_currency=settings.BASE_CURRENCY,
    )


@router.get("/allocation", response_model=AllocationComparison)
def get_allocation_comparison(db: Session = Depends(get_db)):
    """Get current asset allocation vs strategic allocation."""
    data = svc_allocation_comparison(db)
    return AllocationComparison(
        allocations=[AllocationResponse(**a) for a in data["allocations"]],
        total_value=data["total_value"],
    )


@router.get("/returns/twrr", response_model=TWRRResponse)
def calculate_twrr(
    start_date: date = None, end_date: date = None, db: Session = Depends(get_db)
):
    """Calculate Time-Weighted Rate of Return (TWRR)."""
    from app.models.transaction import Transaction

    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - relativedelta(years=1)

    snapshots = (
        db.query(MonthlySnapshot)
        .filter(
            MonthlySnapshot.snapshot_date >= start_date,
            MonthlySnapshot.snapshot_date <= end_date,
        )
        .order_by(MonthlySnapshot.snapshot_date)
        .all()
    )

    if len(snapshots) < 2:
        return TWRRResponse(
            twrr=0.0, annualized_twrr=0.0, period_start=start_date, period_end=end_date
        )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )
        .order_by(Transaction.transaction_date)
        .all()
    )

    cash_flows = {}
    for txn in transactions:
        txn_date = txn.transaction_date
        if txn_date not in cash_flows:
            cash_flows[txn_date] = 0.0
        amount = float(txn.amount) * get_exchange_rate(db, txn.currency)
        if txn.transaction_type in ["deposit", "transfer_in"]:
            cash_flows[txn_date] += amount
        elif txn.transaction_type in ["withdrawal", "transfer_out"]:
            cash_flows[txn_date] -= amount

    sub_period_returns = []
    cumulative_return = 1.0

    for i in range(1, len(snapshots)):
        prev_snapshot = snapshots[i - 1]
        curr_snapshot = snapshots[i]
        beginning_value = float(prev_snapshot.net_worth)
        ending_value = float(curr_snapshot.net_worth)

        period_cash_flow = 0.0
        for cf_date, cf_amount in cash_flows.items():
            if prev_snapshot.snapshot_date < cf_date <= curr_snapshot.snapshot_date:
                period_cash_flow += cf_amount

        if beginning_value > 0:
            hpr = (ending_value - period_cash_flow) / beginning_value - 1
        else:
            hpr = 0.0

        sub_period_returns.append(
            {
                "period_start": prev_snapshot.snapshot_date.isoformat(),
                "period_end": curr_snapshot.snapshot_date.isoformat(),
                "return": hpr * 100,
            }
        )
        cumulative_return *= 1 + hpr

    twrr = (cumulative_return - 1) * 100
    days = (end_date - start_date).days
    years = days / 365.25
    if years > 0 and cumulative_return > 0:
        annualized_twrr = (pow(cumulative_return, 1 / years) - 1) * 100
    else:
        annualized_twrr = 0.0

    return TWRRResponse(
        twrr=twrr,
        annualized_twrr=annualized_twrr,
        period_start=start_date,
        period_end=end_date,
        sub_period_returns=sub_period_returns,
    )


@router.get("/yield", response_model=YieldResponse)
def calculate_yield(
    start_date: date = None, end_date: date = None, db: Session = Depends(get_db)
):
    """Calculate investment yield (income / average portfolio value)."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - relativedelta(years=1)

    income_records = (
        db.query(Income)
        .filter(Income.income_date >= start_date, Income.income_date <= end_date)
        .all()
    )

    total_income = 0.0
    for record in income_records:
        total_income += float(record.amount) * get_exchange_rate(db, record.currency)

    snapshots = (
        db.query(MonthlySnapshot)
        .filter(
            MonthlySnapshot.snapshot_date >= start_date,
            MonthlySnapshot.snapshot_date <= end_date,
        )
        .all()
    )

    if snapshots:
        avg_value = sum(float(s.net_worth) for s in snapshots) / len(snapshots)
    else:
        nw = calculate_networth(db)
        avg_value = nw["net_worth"]

    yield_percentage = (total_income / avg_value * 100) if avg_value > 0 else 0.0
    days = (end_date - start_date).days
    annualized_yield = yield_percentage * (365 / days) if days > 0 else 0.0

    return YieldResponse(
        total_income=total_income,
        average_portfolio_value=avg_value,
        yield_percentage=yield_percentage,
        period_start=start_date,
        period_end=end_date,
        annualized_yield=annualized_yield,
    )


@router.get("/returns/modified-dietz", response_model=ModifiedDietzResponse)
def calculate_modified_dietz(
    start_date: date = None,
    end_date: date = None,
    asset_class_id: str = None,
    db: Session = Depends(get_db),
):
    """Calculate Modified Dietz return for the portfolio or a single asset class."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, 1, 1)

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

    per_class = None
    if not ac_id:
        from app.models.asset import AssetClass

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
                db,
                begin_snapshot.snapshot_date,
                end_snapshot.snapshot_date,
                total_days,
                ac.id,
            )
            c_income = compute_period_income(
                db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, ac.id
            )
            c_ret = compute_modified_dietz(c_beg, c_end, c_cf, c_income, c_wcf)
            per_class.append(
                AssetClassReturn(
                    asset_class_id=ac.id,
                    asset_class_name=ac.name,
                    beginning_market_value=c_beg,
                    ending_market_value=c_end,
                    net_cashflow=c_cf,
                    income=c_income,
                    weighted_cashflow=c_wcf,
                    return_percentage=c_ret,
                )
            )

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
def get_daily_performance_series_endpoint(
    start_date: date = None,
    end_date: date = None,
    asset_class_id: str = None,
    db: Session = Depends(get_db),
):
    """Generate a daily step-function cumulative return series."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, 1, 1)

    from uuid import UUID as PyUUID
    from datetime import timedelta
    from app.models.asset import AssetClass

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

    snapshot_returns = {}
    for snap in snapshots_in_range:
        total_days = (snap.snapshot_date - baseline.snapshot_date).days
        if total_days <= 0:
            continue
        end_mv = get_snapshot_market_value_by_class(db, snap, ac_id)
        net_cf, weighted_cf = compute_weighted_cashflows(
            db, baseline.snapshot_date, snap.snapshot_date, total_days, ac_id
        )
        inc = compute_period_income(
            db, baseline.snapshot_date, snap.snapshot_date, ac_id
        )
        ret = compute_modified_dietz(beg_mv, end_mv, net_cf, inc, weighted_cf)
        snapshot_returns[snap.snapshot_date] = ret

    series = []
    current_return = 0.0
    day = start_date
    while day <= end_date:
        if day in snapshot_returns:
            current_return = snapshot_returns[day]
        series.append(
            DailyReturnPoint(date=day, cumulative_return=round(current_return, 4))
        )
        day += timedelta(days=1)

    return DailyPerformanceSeriesResponse(
        series=series,
        period_start=start_date,
        period_end=end_date,
        asset_class_id=ac_id,
        asset_class_name=ac_name,
    )
