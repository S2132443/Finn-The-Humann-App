-- Migration 003: Add market_prices table for price tracking and watchlist
-- Safe to run multiple times (idempotent)

CREATE TABLE IF NOT EXISTS market_prices (
    symbol VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    asset_class_id UUID REFERENCES asset_classes(id),
    current_price DECIMAL(20, 8),
    previous_price DECIMAL(20, 8),
    currency VARCHAR(3) DEFAULT 'MYR',
    price_myr DECIMAL(20, 2),
    source VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed from existing assets that have symbols
INSERT INTO market_prices (symbol, name, asset_class_id, currency, source)
SELECT DISTINCT ON (a.symbol)
    a.symbol,
    a.name,
    a.asset_class_id,
    a.currency,
    CASE WHEN ac.name IN ('Bitcoin', 'Altcoin') THEN 'luno' ELSE 'yahoo' END
FROM assets a
LEFT JOIN asset_classes ac ON a.asset_class_id = ac.id
WHERE a.symbol IS NOT NULL AND a.symbol != '' AND a.is_active = true
ON CONFLICT (symbol) DO NOTHING;
