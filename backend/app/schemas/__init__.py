"""Pydantic schemas for API validation and serialization."""

from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTypeResponse,
    AccountWithAssets,
)
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetClassResponse,
    AssetClassCreate,
)
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.income import IncomeCreate, IncomeResponse, IncomeSummary
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse, SnapshotSummary
from app.schemas.allocation import (
    AllocationResponse,
    AllocationComparison,
    StrategicAllocationCreate,
    StrategicAllocationResponse,
)
from app.schemas.calculations import (
    NetWorthResponse,
    NetWorthHistory,
    TWRRResponse,
    YieldResponse,
)
from app.schemas.currency import CurrencyResponse

__all__ = [
    "AccountCreate",
    "AccountUpdate",
    "AccountResponse",
    "AccountTypeResponse",
    "AccountWithAssets",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetClassResponse",
    "AssetClassCreate",
    "TransactionCreate",
    "TransactionResponse",
    "IncomeCreate",
    "IncomeResponse",
    "IncomeSummary",
    "SnapshotCreate",
    "SnapshotResponse",
    "SnapshotSummary",
    "AllocationResponse",
    "AllocationComparison",
    "StrategicAllocationCreate",
    "StrategicAllocationResponse",
    "NetWorthResponse",
    "NetWorthHistory",
    "TWRRResponse",
    "YieldResponse",
    "CurrencyResponse",
]
