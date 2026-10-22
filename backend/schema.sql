-- ====================================================================
-- BillBuddy - Supabase Database Schema & Storage Setup
-- ====================================================================
-- Run this script in your Supabase SQL Editor:
-- (Supabase Dashboard -> SQL Editor -> New Query -> Paste & Run)
-- ====================================================================

-- 1. Enable UUID Extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create 'products' Table
CREATE TABLE IF NOT EXISTS public.products (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    user_id TEXT NOT NULL,
    user_email TEXT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Electronics',
    price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    warranty_months INTEGER NOT NULL DEFAULT 12,
    purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
    emoji TEXT DEFAULT '📦',
    bill_name TEXT,
    bill_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for lightning fast queries
CREATE INDEX IF NOT EXISTS idx_products_user_id ON public.products(user_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_purchase_date ON public.products(purchase_date);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON public.products(created_at DESC);

-- 3. Create 'users' Table (For syncing Google Auth profiles)
CREATE TABLE IF NOT EXISTS public.users (
    id TEXT PRIMARY KEY, -- Firebase UID
    email TEXT NOT NULL,
    name TEXT,
    avatar_url TEXT,
    last_sign_in TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Permissive policy for API key access
-- (Allows backend service or anon key to query and insert user-scoped rows)
DROP POLICY IF EXISTS "Allow all operations for service role and anon" ON public.products;
CREATE POLICY "Allow all operations for service role and anon"
    ON public.products
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations on users" ON public.users;
CREATE POLICY "Allow all operations on users"
    ON public.users
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 5. Supabase Storage Bucket Setup
-- Create the 'bills' bucket for invoice PDFs and receipts
INSERT INTO storage.buckets (id, name, public)
VALUES ('bills', 'bills', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Policy to allow public reads for uploaded bills/invoices
DROP POLICY IF EXISTS "Public Access to Bills" ON storage.objects;
CREATE POLICY "Public Access to Bills"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'bills');

-- Policy to allow uploading bills/invoices
DROP POLICY IF EXISTS "Allow bill uploads" ON storage.objects;
CREATE POLICY "Allow bill uploads"
    ON storage.objects FOR INSERT
    WITH CHECK (bucket_id = 'bills');

-- Policy to allow deleting bills
DROP POLICY IF EXISTS "Allow bill deletes" ON storage.objects;
CREATE POLICY "Allow bill deletes"
    ON storage.objects FOR DELETE
    USING (bucket_id = 'bills');

-- Done! Your Supabase database and storage are now fully set up for BillBuddy.
