-- Migration: Add asset_class_id column to transactions table
-- This column was defined in init.sql but may be missing in existing databases

ALTER TABLE transactions ADD COLUMN IF NOT EXISTS asset_class_id UUID REFERENCES asset_classes(id);
CREATE INDEX IF NOT EXISTS idx_transactions_asset_class ON transactions(asset_class_id);
