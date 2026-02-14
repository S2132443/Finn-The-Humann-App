"""Price fetching service for on-demand price updates."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx
import yfinance as yf
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetClass
from app.models.currency import Currency
from app.models.market_price import MarketPrice

logger = logging.getLogger(__name__)

# Asset class names (must match init.sql seeds)
CLASS_BITCOIN = "Bitcoin"
CLASS_ALTCOIN = "Altcoin"
CLASS_MY_EQUITIES = "MY Equities"
CLASS_US_EQUITIES = "US Equities"
CLASS_GOLD = "Gold"

# LUNO pair mapping: symbol -> LUNO pair code
# Reverse map built from pair codes (e.g. XBTMYR -> BTC, ETHMYR -> ETH)
LUNO_SYMBOL_TO_PAIR = {
    "BTC": "XBTMYR",
    "XBT": "XBTMYR",
    "ETH": "ETHMYR",
    "XRP": "XRPMYR",
    "SOL": "SOLMYR",
    "ADA": "ADAMYR",
    "LINK": "LINKMYR",
    "UNI": "UNIMYR",
    "LTC": "LTCMYR",
    "BCH": "BCHMYR",
    "POL": "POLMYR",
    "MATIC": "POLMYR",
    "AVAX": "AVAXMYR",
    "ATOM": "ATOMMYR",
    "NEAR": "NEARMYR",
    "ALGO": "ALGOMYR",
}

# Reverse: pair code -> canonical symbol
LUNO_PAIR_TO_SYMBOL = {}
for sym, pair in LUNO_SYMBOL_TO_PAIR.items():
    if pair not in LUNO_PAIR_TO_SYMBOL:
        LUNO_PAIR_TO_SYMBOL[pair] = sym


async def fetch_luno_prices() -> dict[str, float]:
    """Fetch all MYR crypto prices from LUNO in a single API call.

    Returns {symbol: price_in_myr} e.g. {'BTC': 453231.0, 'ETH': 15200.0}
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get("https://api.luno.com/api/1/tickers")
            resp.raise_for_status()
            data = resp.json()

        results = {}
        for ticker in data.get("tickers", []):
            pair = ticker.get("pair", "")
            if pair.endswith("MYR") and pair in LUNO_PAIR_TO_SYMBOL:
                price = ticker.get("last_trade")
                if price:
                    symbol = LUNO_PAIR_TO_SYMBOL[pair]
                    results[symbol] = float(price)
        return results
    except Exception as e:
        logger.error(f"LUNO fetch failed: {e}")
        return {}


def fetch_yahoo_prices(symbols: list[str]) -> dict[str, float]:
    """Fetch prices from Yahoo Finance in a single batch call.

    Symbols should include suffixes (e.g. '1155.KL' for MY stocks).
    Returns {symbol: price}.
    """
    if not symbols:
        return {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        results = {}
        for sym in symbols:
            try:
                ticker = tickers.tickers.get(sym)
                if ticker:
                    price = getattr(ticker.fast_info, "last_price", None)
                    if price and price > 0:
                        results[sym] = float(price)
            except Exception as e:
                logger.error(f"yfinance failed for {sym}: {e}")
        return results
    except Exception as e:
        logger.error(f"yfinance batch fetch failed: {e}")
        return {}


async def fetch_exchange_rates() -> dict[str, float]:
    """Fetch exchange rates from free API. Returns {currency_code: rate_to_myr}.

    e.g. {'USD': 4.47, 'SGD': 3.31, 'MYR': 1.0}
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/MYR")
            resp.raise_for_status()
            data = resp.json()

        if data.get("result") != "success":
            logger.error(f"Exchange rate API error: {data}")
            return {}

        # API returns: 1 MYR = X foreign. We need: 1 foreign = Y MYR (Y = 1/X).
        rates = {"MYR": 1.0}
        for code, rate in data.get("rates", {}).items():
            if rate > 0:
                rates[code] = 1.0 / rate
        return rates
    except Exception as e:
        logger.error(f"Exchange rate fetch failed: {e}")
        return {}


def _resolve_yahoo_symbol(symbol: str, class_name: str) -> Optional[str]:
    """Map an asset symbol to a Yahoo Finance ticker."""
    if not symbol:
        return None
    symbol = symbol.strip()
    if class_name == CLASS_MY_EQUITIES:
        return symbol if symbol.endswith(".KL") else f"{symbol}.KL"
    elif class_name == CLASS_US_EQUITIES:
        return symbol
    elif class_name == CLASS_GOLD:
        return "GC=F"
    return None


async def update_exchange_rates(db: Session) -> dict:
    """Update all currencies in the database from the exchange rate API."""
    result = {"updated": 0, "errors": []}
    rates = await fetch_exchange_rates()
    if not rates:
        result["errors"].append("Failed to fetch exchange rates")
        return result

    currencies = db.query(Currency).all()
    for currency in currencies:
        if currency.code in rates:
            currency.exchange_rate_to_myr = Decimal(str(round(rates[currency.code], 6)))
            result["updated"] += 1

    db.commit()
    return result


async def update_all_prices(db: Session) -> dict:
    """Fetch and update prices for all tracked symbols in market_prices,
    then push updated prices to matching portfolio assets.

    Returns {updated, failed, skipped, errors, timestamp}.
    """
    result = {
        "updated": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Load all market_prices rows
    tracked = db.query(MarketPrice).all()
    if not tracked:
        return result

    # Build asset_class_id -> name lookup
    class_map = {}
    for ac in db.query(AssetClass).all():
        class_map[ac.id] = ac.name

    # Group by source
    luno_symbols = []   # [(MarketPrice, class_name)]
    yahoo_entries = []  # [(MarketPrice, class_name, yahoo_symbol)]

    for mp in tracked:
        class_name = class_map.get(mp.asset_class_id, "")
        if mp.source == "luno":
            luno_symbols.append((mp, class_name))
        elif mp.source == "yahoo":
            ysym = _resolve_yahoo_symbol(mp.symbol, class_name)
            if ysym:
                yahoo_entries.append((mp, class_name, ysym))
            else:
                result["skipped"] += 1
        else:
            result["skipped"] += 1

    # Get USD→MYR rate for gold conversion
    usd_to_myr = 1.0
    usd_currency = db.query(Currency).filter(Currency.code == "USD").first()
    if usd_currency and usd_currency.exchange_rate_to_myr:
        usd_to_myr = float(usd_currency.exchange_rate_to_myr)

    # --- Fetch LUNO prices (one API call) ---
    luno_prices = await fetch_luno_prices()
    for mp, class_name in luno_symbols:
        sym = mp.symbol.upper()
        # Try both the symbol and common aliases
        price = luno_prices.get(sym)
        if sym == "BTC" and price is None:
            price = luno_prices.get("XBT")
        if price is not None:
            mp.previous_price = mp.current_price
            mp.current_price = Decimal(str(price))
            mp.price_myr = Decimal(str(round(price, 2)))
            result["updated"] += 1
        else:
            result["failed"] += 1
            result["errors"].append(f"LUNO: {mp.name} ({mp.symbol})")

    # --- Fetch Yahoo prices (one batch call) ---
    yahoo_symbol_list = [entry[2] for entry in yahoo_entries]
    yahoo_prices = fetch_yahoo_prices(yahoo_symbol_list) if yahoo_symbol_list else {}

    for mp, class_name, ysym in yahoo_entries:
        price = yahoo_prices.get(ysym)
        if price is not None:
            mp.previous_price = mp.current_price
            if class_name == CLASS_GOLD:
                # Yahoo gold is USD per troy oz; convert to MYR per gram
                price_myr_per_gram = (price * usd_to_myr) / 31.1035
                mp.current_price = Decimal(str(round(price_myr_per_gram, 2)))
                mp.price_myr = mp.current_price
            elif class_name == CLASS_US_EQUITIES:
                # US stocks are in USD; store USD price, convert to MYR
                mp.current_price = Decimal(str(round(price, 4)))
                mp.price_myr = Decimal(str(round(price * usd_to_myr, 2)))
            else:
                # MY stocks are already in MYR
                mp.current_price = Decimal(str(round(price, 4)))
                mp.price_myr = Decimal(str(round(price, 2)))
            result["updated"] += 1
        else:
            result["failed"] += 1
            result["errors"].append(f"Yahoo: {mp.name} ({ysym})")

    db.commit()

    # --- Push prices to portfolio assets ---
    updated_symbols = {
        mp.symbol: mp for mp in tracked if mp.current_price is not None
    }
    if updated_symbols:
        assets = (
            db.query(Asset)
            .filter(Asset.is_active == True, Asset.symbol.in_(updated_symbols.keys()))
            .all()
        )
        for asset in assets:
            mp = updated_symbols.get(asset.symbol)
            if mp:
                asset.current_price = mp.current_price
                if asset.quantity and asset.quantity > 0:
                    asset.current_value = Decimal(str(
                        round(float(asset.quantity) * float(mp.current_price), 2)
                    ))
        db.commit()

    return result
