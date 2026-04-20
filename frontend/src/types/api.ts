/**
 * API Type Definitions for Finn
 */

export interface Account {
  id: string;
  name: string;
  type: string;
  balance: number;
  currency: string;
  broker_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  symbol: string;
  name: string;
  asset_class: string;
  quantity: number;
  cost_basis: number;
  current_price: number;
  currency: string;
  account_id: string;
  pl_amount: number;
  pl_percentage: number;
  market_value: number;
  created_at: string;
  updated_at: string;
}

export interface MarketItem {
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  change_percentage_24h: number;
  currency: string;
  last_updated: string;
}

export interface Broker {
  id: string;
  name: string;
  provider: string;
  status: 'connected' | 'disconnected' | 'error';
  last_sync?: string;
}

export interface Transaction {
  id: string;
  date: string;
  asset_id?: string;
  account_id: string;
  type: 'buy' | 'sell' | 'dividend' | 'deposit' | 'withdrawal' | 'fee';
  amount: number;
  quantity?: number;
  price?: number;
  currency: string;
  description?: string;
  asset_class?: string;
}

export interface Income {
  id: string;
  date: string;
  amount: number;
  currency: string;
  type: 'dividend' | 'interest' | 'rental' | 'salary' | 'other';
  source: string;
  account_id: string;
}

export interface IncomeSummary {
  total_income: number;
  by_type: Record<string, number>;
  monthly_history: { month: string; amount: number }[];
}

export interface NetWorth {
  total_net_worth: number;
  currency: string;
  assets_total: number;
  liabilities_total: number;
}

export interface NetWorthHistory {
  date: string;
  value: number;
}

export interface Allocation {
  asset_class: string;
  value: number;
  percentage: number;
}

export interface AllocationComparison {
  asset_class: string;
  actual_percentage: number;
  target_percentage: number;
}

export interface Returns {
  twrr: number;
  modified_dietz: number;
  daily_series: { date: string; value: number }[];
}

export interface Snapshot {
  id: string;
  date: string;
  net_worth: number;
  total_assets: number;
  total_liabilities: number;
}

export interface Settings {
  asset_classes: string[];
  currencies: string[];
  saa: Record<string, number>; // Strategic Asset Allocation
}
