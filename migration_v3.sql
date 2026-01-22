-- V3 Migration: Financial Control & Pacing
-- Run this in Supabase SQL Editor

-- 1. Add Installment Support to finance_transactions
ALTER TABLE finance_transactions 
ADD COLUMN IF NOT EXISTS installment_current int,
ADD COLUMN IF NOT EXISTS installment_total int,
ADD COLUMN IF NOT EXISTS original_desc text;

-- 2. Create Budgets Table
CREATE TABLE IF NOT EXISTS budgets (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at timestamptz DEFAULT now(),
  category text NOT NULL, -- Matches FinanceEntry categories
  limit_amount numeric NOT NULL,
  alert_threshold numeric DEFAULT 0.9, -- Alert at 90%
  period text DEFAULT 'monthly' -- 'monthly', 'weekly', 'yearly'
);

-- Optional: Index for faster budget lookups
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category);
