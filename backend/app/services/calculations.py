"""Shared calculation functions used by both API and web routes."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from dateutil.relativedelta import relativedelta

from app.models.account import Account
from app.models.asset import Asset, AssetClass
from app.models.transaction import Transaction
from app.models.income import Income
from app.models.snapshot import MonthlySnapshot, AssetSnapshot
from app.models.currency import Currency
from app.models.allocation import StrategicAllocation
from app.config import settings


def get_exchange_rate(db: Session, currency_code: str) -> float:
    """Get exchange rate to MYR for a currency."""
    if currency_code == "MYR":
        return 1.0
    currency = db.query(Currency).filter(Currency.code == currency_code).first()
    return float(currency.exchange_rate_to_myr) if currency else 1.0


def calculate_networth(db: Session) -> dict:
    """Calculate current net worth. Returns dict with total_assets, total_liabilities, net_worth."""
    total_assets = 0.0
    total_liabilities = 0.0

    accounts = db.query(Account).filter(Account.is_active == True).all()
    for account in accounts:
        for asset in account.assets:
            if asset.is_active and asset.current_value:
                value_myr = float(asset.current_value) * get_exchange_rate(
                    db, asset.currency
                )
                if account.is_liability:
                    total_liabilities += value_myr
                else:
                    total_assets += value_myr

    return {
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities,
        "base_currency": settings.BASE_CURRENCY,
        "as_of_date": date.today(),
    }


def get_networth_history(db: Session, months: int = 12) -> list:
    """Get net worth history from monthly snapshots."""
    start_date = date.today() - relativedelta(months=months)
    snapshots = (
        db.query(MonthlySnapshot)
        .filter(MonthlySnapshot.snapshot_date >= start_date)
        .order_by(MonthlySnapshot.snapshot_date)
        .all()
    )
    return [
        {
            "date": s.snapshot_date,
            "total_assets": float(s.total_assets),
            "total_liabilities": float(s.total_liabilities),
            "net_worth": float(s.net_worth),
        }
        for s in snapshots
    ]


def get_allocation_comparison(db: Session) -> dict:
    """Get current asset allocation vs strategic allocation."""
    asset_classes = (
        db.query(AssetClass)
        .filter(AssetClass.is_active == True)
        .order_by(AssetClass.display_order)
        .all()
    )

    total_portfolio_value = 0.0
    class_values = {}

    for asset_class in asset_classes:
        class_value = 0.0
        assets = (
            db.query(Asset)
            .filter(Asset.asset_class_id == asset_class.id, Asset.is_active == True)
            .all()
        )
        for asset in assets:
            if asset.current_value:
                account = (
                    db.query(Account)
                    .filter(
                        Account.id == asset.account_id,
                        Account.is_active == True,
                        Account.is_liability == False,
                    )
                    .first()
                )
                if account:
                    value_myr = float(asset.current_value) * get_exchange_rate(
                        db, asset.currency
                    )
                    class_value += value_myr
        class_values[asset_class.id] = class_value
        total_portfolio_value += class_value

    allocations = []
    for asset_class in asset_classes:
        class_value = class_values[asset_class.id]
        percentage = (
            (class_value / total_portfolio_value * 100)
            if total_portfolio_value > 0
            else 0
        )

        strategic = (
            db.query(StrategicAllocation)
            .filter(
                StrategicAllocation.asset_class_id == asset_class.id,
                StrategicAllocation.effective_date <= date.today(),
            )
            .order_by(StrategicAllocation.effective_date.desc())
            .first()
        )
        target_percentage = float(strategic.target_percentage) if strategic else 0.0

        allocations.append(
            {
                "asset_class_id": asset_class.id,
                "asset_class_name": asset_class.name,
                "color": asset_class.color,
                "total_value": class_value,
                "percentage": percentage,
                "target_percentage": target_percentage,
            }
        )

    return {"allocations": allocations, "total_value": total_portfolio_value}


def get_income_summary(db: Session) -> dict:
    """Get income summary grouped by type and asset class."""
    income_records = db.query(Income).all()

    by_type = {}
    by_asset_class = {}
    total = 0.0

    for record in income_records:
        amount_myr = float(record.amount) * get_exchange_rate(db, record.currency)
        total += amount_myr

        inc_type = record.income_type
        by_type[inc_type] = by_type.get(inc_type, 0) + amount_myr

        if record.asset and record.asset.asset_class:
            class_name = record.asset.asset_class.name
            by_asset_class[class_name] = by_asset_class.get(class_name, 0) + amount_myr

    return {"total": total, "by_type": by_type, "by_asset_class": by_asset_class}


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
) -> tuple:
    """Compute net cashflow and time-weighted cashflow for the period."""
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
            signed_amount = -amount_myr

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
        query = query.join(Income.asset).filter(Asset.asset_class_id == asset_class_id)

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


def find_snapshot_on_or_before(db: Session, target_date: date):
    """Find the closest snapshot on or before the given date."""
    return (
        db.query(MonthlySnapshot)
        .filter(MonthlySnapshot.snapshot_date <= target_date)
        .order_by(MonthlySnapshot.snapshot_date.desc())
        .first()
    )


def calculate_modified_dietz_return(
    db: Session, start_date=None, end_date=None, asset_class_id=None
) -> dict:
    """Calculate Modified Dietz return for the portfolio or a single asset class."""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, 1, 1)

    from uuid import UUID as PyUUID

    ac_id = None
    if asset_class_id:
        try:
            ac_id = PyUUID(str(asset_class_id))
        except ValueError:
            ac_id = None

    begin_snapshot = find_snapshot_on_or_before(db, start_date)
    end_snapshot = find_snapshot_on_or_before(db, end_date)

    if not begin_snapshot or not end_snapshot or begin_snapshot.id == end_snapshot.id:
        return {
            "return_percentage": 0.0,
            "beginning_market_value": 0.0,
            "ending_market_value": 0.0,
            "net_cashflow": 0.0,
            "income": 0.0,
            "weighted_cashflow": 0.0,
            "period_start": start_date,
            "period_end": end_date,
            "total_days": 0,
            "per_class_returns": None,
        }

    total_days = (end_snapshot.snapshot_date - begin_snapshot.snapshot_date).days
    if total_days <= 0:
        total_days = 1

    beg_mv = get_snapshot_market_value_by_class(db, begin_snapshot, ac_id)
    end_mv = get_snapshot_market_value_by_class(db, end_snapshot, ac_id)
    net_cf, weighted_cf = compute_weighted_cashflows(
        db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, total_days, ac_id
    )
    inc = compute_period_income(
        db, begin_snapshot.snapshot_date, end_snapshot.snapshot_date, ac_id
    )
    return_pct = compute_modified_dietz(beg_mv, end_mv, net_cf, inc, weighted_cf)

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
                {
                    "asset_class_id": ac.id,
                    "asset_class_name": ac.name,
                    "beginning_market_value": c_beg,
                    "ending_market_value": c_end,
                    "net_cashflow": c_cf,
                    "income": c_income,
                    "weighted_cashflow": c_wcf,
                    "return_percentage": c_ret,
                }
            )

    return {
        "return_percentage": return_pct,
        "beginning_market_value": beg_mv,
        "ending_market_value": end_mv,
        "net_cashflow": net_cf,
        "income": inc,
        "weighted_cashflow": weighted_cf,
        "period_start": start_date,
        "period_end": end_date,
        "total_days": total_days,
        "per_class_returns": per_class,
    }


def get_daily_performance_series(
    db: Session, start_date=None, end_date=None, asset_class_id=None
) -> dict:
    """Generate a daily step-function cumulative return series."""
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
            ac_id = PyUUID(str(asset_class_id))
        except ValueError:
            ac_id = None
        if ac_id:
            ac_obj = db.query(AssetClass).filter(AssetClass.id == ac_id).first()
            if ac_obj:
                ac_name = ac_obj.name

    baseline = find_snapshot_on_or_before(db, start_date)
    if not baseline:
        return {
            "series": [],
            "period_start": start_date,
            "period_end": end_date,
            "asset_class_id": ac_id,
            "asset_class_name": ac_name,
        }

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
        series.append({"date": day, "cumulative_return": round(current_return, 4)})
        day += timedelta(days=1)

    return {
        "series": series,
        "period_start": start_date,
        "period_end": end_date,
        "asset_class_id": ac_id,
        "asset_class_name": ac_name,
    }
