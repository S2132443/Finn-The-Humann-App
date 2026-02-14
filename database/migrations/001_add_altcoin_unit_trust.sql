-- Migration 001: Add Altcoin and Unit Trust asset classes
-- Safe to run multiple times (idempotent)

-- Add new asset classes
INSERT INTO asset_classes (name, description, color, display_order)
VALUES ('Altcoin', 'Alternative cryptocurrencies (ETH, SOL, etc.)', '#8b5cf6', 5)
ON CONFLICT (name) DO NOTHING;

INSERT INTO asset_classes (name, description, color, display_order)
VALUES ('Unit Trust', 'Unit trust and mutual funds', '#e377c2', 9)
ON CONFLICT (name) DO NOTHING;

-- Update display_orders to accommodate new classes
UPDATE asset_classes SET display_order = 6 WHERE name = 'Cash';
UPDATE asset_classes SET display_order = 7 WHERE name = 'Fixed Income';
UPDATE asset_classes SET display_order = 8 WHERE name = 'Real Estate';
UPDATE asset_classes SET display_order = 10 WHERE name = 'Others';
