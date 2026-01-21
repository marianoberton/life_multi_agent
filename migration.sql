-- Migration to add new columns to finance_transactions table
-- Run this in your Supabase SQL Editor

ALTER TABLE finance_transactions
ADD COLUMN IF NOT EXISTS payment_method text,
ADD COLUMN IF NOT EXISTS is_client_expense boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS subcategory text; 
-- Note: 'subcategory' was requested in the prompt ("actualizar la tabla ... con las nuevas columnas (subcategory...)")
-- even though we are storing the full "Category: Subcategory" string in the 'category' column for now.
-- You might want to split it later or just use 'category' for the full string.
