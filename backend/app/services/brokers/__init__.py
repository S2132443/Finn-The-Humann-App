"""Broker integration framework.

Provider-based architecture for syncing balances from external brokers.
Each broker is a separate module that registers itself with the provider registry.

Adding a new broker:
1. Create a new file in this directory (e.g. moomoo.py)
2. Implement a class inheriting from BrokerProvider
3. Call register_provider() at module level
4. Import the module in main.py to trigger registration
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.asset import Asset, AssetClass
from app.models.market_price import MarketPrice

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a broker balance sync."""

    provider: str = ""
    synced: int = 0
    created: int = 0
    zeroed: int = 0
    errors: list[str] = field(default_factory=list)


class BrokerProvider(ABC):
    """Base class for broker integrations."""

    name: str = ""
    display_name: str = ""
    config_keys: list[str] = []

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if required API keys/config are set."""
        ...

    @abstractmethod
    def sync_balances(self, db: Session) -> SyncResult:
        """Pull balances from the broker and create/update assets."""
        ...


# --- Provider Registry ---

PROVIDERS: dict[str, BrokerProvider] = {}


def register_provider(provider: BrokerProvider):
    """Register a broker provider. Called at module import time."""
    PROVIDERS[provider.name] = provider
    logger.info(f"Registered broker provider: {provider.display_name}")


def get_provider(name: str) -> BrokerProvider | None:
    return PROVIDERS.get(name)


def get_all_providers() -> list[BrokerProvider]:
    return list(PROVIDERS.values())


def get_configured_providers() -> list[BrokerProvider]:
    return [p for p in PROVIDERS.values() if p.is_configured()]


# --- Shared Helpers (reused by all providers) ---

_LUNO_CLASSES = {"Bitcoin", "Altcoin"}


def find_or_create_account(
    db: Session,
    institution: str,
    name: str,
    currency: str = "MYR",
) -> Account:
    """Find an existing account by institution or create a new one."""
    account = (
        db.query(Account)
        .filter(Account.institution.ilike(institution), Account.is_active == True)
        .first()
    )
    if not account:
        account = Account(
            name=name,
            institution=institution,
            currency=currency,
        )
        db.add(account)
        db.flush()
        logger.info(f"Auto-created account: {name} ({institution})")
    return account


def upsert_asset(
    db: Session,
    account_id,
    symbol: str,
    name: str,
    quantity: float,
    asset_class_id,
    currency: str = "MYR",
) -> tuple[Asset, bool]:
    """Find existing asset by symbol+account or create new. Returns (asset, is_new)."""
    asset = (
        db.query(Asset)
        .filter(
            Asset.symbol == symbol,
            Asset.account_id == account_id,
            Asset.is_active == True,
        )
        .first()
    )
    is_new = False
    if asset:
        asset.quantity = quantity
        if asset.current_price and asset.current_price > 0:
            asset.current_value = round(quantity * float(asset.current_price), 2)
    else:
        asset = Asset(
            account_id=account_id,
            asset_class_id=asset_class_id,
            name=name,
            symbol=symbol,
            quantity=quantity,
            currency=currency,
        )
        db.add(asset)
        is_new = True
    return asset, is_new


def sync_market_price(db: Session, asset: Asset):
    """Auto-create a market_prices row for an asset with a symbol.

    Shared version of the logic from web/assets.py for use by brokers.
    """
    if not asset.symbol:
        return
    existing = db.query(MarketPrice).filter(MarketPrice.symbol == asset.symbol).first()
    if existing:
        return
    class_name = asset.asset_class.name if asset.asset_class else ""
    source = "luno" if class_name in _LUNO_CLASSES else "yahoo"
    mp = MarketPrice(
        symbol=asset.symbol,
        name=asset.name,
        asset_class_id=asset.asset_class_id,
        currency=asset.currency,
        source=source,
    )
    db.add(mp)
