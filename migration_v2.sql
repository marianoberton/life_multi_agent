-- V2 Migration for Granular Finance Tracking
-- Run this in Supabase SQL Editor

-- 1. Add subcategory column
ALTER TABLE finance_transactions 
ADD COLUMN IF NOT EXISTS subcategory text;

-- 2. Add payment_method column
ALTER TABLE finance_transactions 
ADD COLUMN IF NOT EXISTS payment_method text;

-- 3. Add is_client_expense column
ALTER TABLE finance_transactions 
ADD COLUMN IF NOT EXISTS is_client_expense boolean DEFAULT false;

-- 4. Add is_fixed column (if not already present)
ALTER TABLE finance_transactions 
ADD COLUMN IF NOT EXISTS is_fixed boolean DEFAULT false;

-- Optional: Create an index on category/subcategory for faster reporting
CREATE INDEX IF NOT EXISTS idx_finance_category ON finance_transactions(category);
CREATE INDEX IF NOT EXISTS idx_finance_subcategory ON finance_transactions(subcategory);
