-- Finn Investment Tracking Platform - Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- LOOKUP TABLES
-- =============================================

-- Asset Classes (configurable)
CREATE TABLE asset_classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6c757d', -- Hex color for charts
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Account Types
CREATE TABLE account_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Currencies
CREATE TABLE currencies (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10),
    exchange_rate_to_myr DECIMAL(15, 6) DEFAULT 1.0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- CORE TABLES
-- =============================================

-- Accounts (Trading accounts, Savings, Crypto wallets, etc.)
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    account_type_id UUID REFERENCES account_types(id),
    institution VARCHAR(255),
    account_number VARCHAR(100),
    currency VARCHAR(3) REFERENCES currencies(code) DEFAULT 'MYR',
    is_liability BOOLEAN DEFAULT false,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assets (Individual holdings)
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    asset_class_id UUID REFERENCES asset_classes(id),
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50),
    quantity DECIMAL(20, 8) DEFAULT 0,
    current_price DECIMAL(20, 8),
    current_value DECIMAL(20, 2),
    currency VARCHAR(3) REFERENCES currencies(code) DEFAULT 'MYR',
    cost_basis DECIMAL(20, 2),
    purchase_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Transactions (Deposits, Withdrawals, Transfers)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL, -- 'deposit', 'withdrawal', 'transfer', 'fee'
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(3) REFERENCES currencies(code) DEFAULT 'MYR',
    transaction_date DATE NOT NULL,
    description TEXT,
    reference VARCHAR(255),
    asset_class_id UUID REFERENCES asset_classes(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Income (Dividends, Rental, Interest, etc.)
CREATE TABLE income (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    income_type VARCHAR(50) NOT NULL, -- 'dividend', 'rental', 'interest', 'distribution'
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(3) REFERENCES currencies(code) DEFAULT 'MYR',
    income_date DATE NOT NULL,
    description TEXT,
    is_reinvested BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Strategic Asset Allocation (Target allocations)
CREATE TABLE strategic_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_class_id UUID REFERENCES asset_classes(id) ON DELETE CASCADE,
    target_percentage DECIMAL(5, 2) NOT NULL,
    effective_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_class_id, effective_date)
);

-- Monthly Snapshots (Historical tracking)
CREATE TABLE monthly_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_date DATE NOT NULL UNIQUE,
    total_assets DECIMAL(20, 2) NOT NULL,
    total_liabilities DECIMAL(20, 2) NOT NULL,
    net_worth DECIMAL(20, 2) NOT NULL,
    allocation_data JSONB, -- Store allocation breakdown as JSON
    performance_data JSONB, -- Store performance metrics as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Asset Snapshots (Historical asset values)
CREATE TABLE asset_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    monthly_snapshot_id UUID REFERENCES monthly_snapshots(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_class_id UUID REFERENCES asset_classes(id),
    value DECIMAL(20, 2) NOT NULL,
    quantity DECIMAL(20, 8),
    currency VARCHAR(3) REFERENCES currencies(code) DEFAULT 'MYR',
    value_in_myr DECIMAL(20, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_assets_account ON assets(account_id);
CREATE INDEX idx_assets_class ON assets(asset_class_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_asset_class ON transactions(asset_class_id);
CREATE INDEX idx_income_account ON income(account_id);
CREATE INDEX idx_income_date ON income(income_date);
CREATE INDEX idx_snapshots_date ON monthly_snapshots(snapshot_date);

-- =============================================
-- INSERT DEFAULT DATA
-- =============================================

-- Default Account Types
INSERT INTO account_types (name, description, icon) VALUES
('Trading Account', 'Stock brokerage and trading accounts', 'chart-line'),
('Savings Account', 'Bank savings and fixed deposits', 'piggy-bank'),
('Crypto Wallet', 'Cryptocurrency wallets and exchanges', 'bitcoin'),
('Real Estate', 'Property investments', 'home'),
('Retirement Fund', 'EPF, PRS, and retirement accounts', 'umbrella'),
('Insurance', 'Investment-linked insurance policies', 'shield'),
('Others', 'Other investment accounts', 'folder');

-- Default Asset Classes
INSERT INTO asset_classes (name, description, color, display_order) VALUES
('MY Equities', 'Malaysian stocks and ETFs', '#1f77b4', 1),
('US Equities', 'US stocks and ETFs', '#ff7f0e', 2),
('Gold', 'Physical gold and gold ETFs', '#ffd700', 3),
('Bitcoin', 'Bitcoin and cryptocurrencies', '#f7931a', 4),
('Cash', 'Cash and money market funds', '#2ca02c', 5),
('Fixed Income', 'Bonds and sukuk', '#9467bd', 6),
('Real Estate', 'REITs and property', '#8c564b', 7),
('Others', 'Other asset classes', '#7f7f7f', 8);

-- Default Currencies
INSERT INTO currencies (code, name, symbol, exchange_rate_to_myr) VALUES
('MYR', 'Malaysian Ringgit', 'RM', 1.000000),
('USD', 'US Dollar', '$', 4.470000),
('SGD', 'Singapore Dollar', 'S$', 3.310000),
('EUR', 'Euro', '€', 4.850000),
('GBP', 'British Pound', '£', 5.650000),
('JPY', 'Japanese Yen', '¥', 0.030000),
('AUD', 'Australian Dollar', 'A$', 2.900000),
('CNY', 'Chinese Yuan', '¥', 0.620000);

-- Default Strategic Allocation (example)
INSERT INTO strategic_allocations (asset_class_id, target_percentage, effective_date, notes)
SELECT id, 
    CASE name
        WHEN 'MY Equities' THEN 45.00
        WHEN 'US Equities' THEN 15.00
        WHEN 'Gold' THEN 10.00
        WHEN 'Bitcoin' THEN 25.00
        WHEN 'Cash' THEN 5.00
        ELSE 0.00
    END,
    '2025-01-01',
    'Initial strategic allocation'
FROM asset_classes
WHERE name IN ('MY Equities', 'US Equities', 'Gold', 'Bitcoin', 'Cash');

-- =============================================
-- FUNCTIONS
-- =============================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers for updated_at
CREATE TRIGGER update_asset_classes_updated_at BEFORE UPDATE ON asset_classes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_currencies_updated_at BEFORE UPDATE ON currencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- VIEWS
-- =============================================

-- View for current net worth
CREATE OR REPLACE VIEW current_net_worth AS
SELECT 
    COALESCE(SUM(CASE WHEN NOT a.is_liability THEN 
        COALESCE(ast.current_value * c.exchange_rate_to_myr, 0) 
    ELSE 0 END), 0) as total_assets,
    COALESCE(SUM(CASE WHEN a.is_liability THEN 
        COALESCE(ast.current_value * c.exchange_rate_to_myr, 0) 
    ELSE 0 END), 0) as total_liabilities,
    COALESCE(SUM(CASE WHEN NOT a.is_liability THEN 
        COALESCE(ast.current_value * c.exchange_rate_to_myr, 0) 
    ELSE 
        -COALESCE(ast.current_value * c.exchange_rate_to_myr, 0) 
    END), 0) as net_worth
FROM accounts a
LEFT JOIN assets ast ON a.id = ast.account_id AND ast.is_active = true
LEFT JOIN currencies c ON ast.currency = c.code
WHERE a.is_active = true;

-- View for current asset allocation
CREATE OR REPLACE VIEW current_allocation AS
SELECT 
    ac.id as asset_class_id,
    ac.name as asset_class_name,
    ac.color,
    COALESCE(SUM(ast.current_value * c.exchange_rate_to_myr), 0) as total_value,
    COALESCE(sa.target_percentage, 0) as target_percentage
FROM asset_classes ac
LEFT JOIN assets ast ON ac.id = ast.asset_class_id AND ast.is_active = true
LEFT JOIN accounts a ON ast.account_id = a.id AND a.is_active = true AND NOT a.is_liability
LEFT JOIN currencies c ON ast.currency = c.code
LEFT JOIN strategic_allocations sa ON ac.id = sa.asset_class_id 
    AND sa.effective_date = (
        SELECT MAX(effective_date) 
        FROM strategic_allocations 
        WHERE asset_class_id = ac.id AND effective_date <= CURRENT_DATE
    )
WHERE ac.is_active = true
GROUP BY ac.id, ac.name, ac.color, sa.target_percentage
ORDER BY ac.display_order;

COMMENT ON DATABASE finn_db IS 'Finn Investment Portfolio Tracking Platform';
