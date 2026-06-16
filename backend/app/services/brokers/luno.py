"""LUNO broker provider — auto-import crypto balances via LUNO API.

Requires read-only API keys set in environment:
  LUNO_API_KEY_ID
  LUNO_API_KEY_SECRET

Generate keys at: https://www.luno.com/wallet/security/api_keys
"""

import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.models.asset import AssetClass
from app.services.brokers import (
    BrokerProvider,
    SyncResult,
    register_provider,
    find_or_create_account,
    upsert_asset,
    sync_market_price,
)

logger = logging.getLogger(__name__)

# LUNO returns "XBT" for Bitcoin; we use "BTC" everywhere else
LUNO_CODE_TO_SYMBOL = {"XBT": "BTC"}

# Display names for auto-created assets
COIN_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "XRP": "Ripple",
    "SOL": "Solana",
    "ADA": "Cardano",
    "LINK": "Chainlink",
    "UNI": "Uniswap",
    "LTC": "Litecoin",
    "BCH": "Bitcoin Cash",
    "POL": "Polygon",
    "AVAX": "Avalanche",
    "ATOM": "Cosmos",
    "NEAR": "NEAR Protocol",
    "ALGO": "Algorand",
    "USDC": "USD Coin",
    "USDT": "Tether",
}

# Fiat codes to skip (not crypto assets)
FIAT_CODES = {"MYR", "IDR", "ZAR", "NGN", "UGX", "EUR", "GBP"}


class LunoProvider(BrokerProvider):
    """LUNO crypto exchange integration."""

    name = "luno"
    display_name = "LUNO"
    config_keys = ["LUNO_API_KEY_ID", "LUNO_API_KEY_SECRET"]

    def is_configured(self) -> bool:
        return bool(settings.LUNO_API_KEY_ID and settings.LUNO_API_KEY_SECRET)

    def sync_balances(self, db: Session) -> SyncResult:
        result = SyncResult(provider=self.name)

        if not self.is_configured():
            result.errors.append("LUNO API keys not configured")
            return result

        try:
            from luno_python.client import Client as LunoClient
        except ImportError:
            result.errors.append("luno-python package not installed")
            return result

        # Look up asset classes for Bitcoin and Altcoin
        btc_class = db.query(AssetClass).filter(AssetClass.name == "Bitcoin").first()
        alt_class = db.query(AssetClass).filter(AssetClass.name == "Altcoin").first()

        # Find or create the LUNO account
        account = find_or_create_account(db, institution="LUNO", name="LUNO")

        # Fetch balances from LUNO
        try:
            client = LunoClient(
                api_key_id=settings.LUNO_API_KEY_ID,
                api_key_secret=settings.LUNO_API_KEY_SECRET,
            )
            response = client.get_balances()
            balances = response.get("balance", [])
        except Exception as e:
            result.errors.append(f"LUNO API error: {e}")
            return result

        # Track which symbols we see from the API
        seen_symbols = set()

        for wallet in balances:
            asset_code = wallet.get("asset", "")
            balance = float(wallet.get("balance", "0"))

            # Skip fiat wallets
            if asset_code in FIAT_CODES:
                continue

            # Map LUNO code to our symbol
            symbol = LUNO_CODE_TO_SYMBOL.get(asset_code, asset_code)
            seen_symbols.add(symbol)

            # Skip zero balances (we'll handle zeroing existing assets below)
            if balance <= 0:
                continue

            # Determine asset class
            asset_class_id = (
                btc_class.id
                if symbol == "BTC" and btc_class
                else (alt_class.id if alt_class else None)
            )

            # Determine display name
            coin_name = COIN_NAMES.get(symbol, symbol)

            # Upsert asset
            asset, is_new = upsert_asset(
                db,
                account_id=account.id,
                symbol=symbol,
                name=coin_name,
                quantity=balance,
                asset_class_id=asset_class_id,
                currency="MYR",
            )

            # Ensure market_prices row exists for price fetching
            sync_market_price(db, asset)

            if is_new:
                result.created += 1
            else:
                result.synced += 1

        # Zero out existing LUNO assets that weren't returned by API
        from app.models.asset import Asset

        existing_assets = (
            db.query(Asset)
            .filter(
                Asset.account_id == account.id,
                Asset.is_active == True,
                Asset.symbol.isnot(None),
            )
            .all()
        )
        for asset in existing_assets:
            if (
                asset.symbol not in seen_symbols
                and asset.quantity
                and float(asset.quantity) > 0
            ):
                asset.quantity = 0
                asset.current_value = 0
                result.zeroed += 1

        db.commit()
        logger.info(
            f"LUNO sync: {result.synced} updated, {result.created} created, "
            f"{result.zeroed} zeroed"
        )
        return result


# Auto-register on import
register_provider(LunoProvider())
